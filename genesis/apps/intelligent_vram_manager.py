"""
Intelligent VRAM Manager for Genesis Hand
基于 IntelligentVRAMNode 的智能显存管理系统
"""

import torch
import psutil
import threading
import time
import logging
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass

# Setup logging
log = logging.getLogger(__name__)

@dataclass
class MemoryStats:
    """内存统计信息"""
    vram_total_mb: float
    vram_used_mb: float
    vram_available_mb: float
    vram_usage_percent: float
    dram_total_mb: float
    dram_used_mb: float
    dram_available_mb: float
    dram_usage_percent: float

class IntelligentVRAMManager:
    """智能 VRAM 管理器"""

    def __init__(self, vram_threshold_percent: float = 50.0):
        self.vram_threshold_percent = vram_threshold_percent
        self.monitoring_active = False
        self.monitoring_thread = None
        self.monitoring_interval = 5.0

        log.info(f"智能 VRAM 管理器已初始化: threshold={vram_threshold_percent}%")

    def get_memory_stats(self) -> MemoryStats:
        """获取当前内存统计"""
        # VRAM 信息
        if torch.cuda.is_available():
            vram_total = torch.cuda.get_device_properties(0).total_memory
            vram_used = torch.cuda.memory_allocated()
            vram_available = vram_total - vram_used
            vram_usage_percent = (vram_used / vram_total) * 100
        else:
            vram_total = vram_used = vram_available = 0
            vram_usage_percent = 0.0

        # DRAM 信息
        dram_info = psutil.virtual_memory()

        return MemoryStats(
            vram_total_mb=vram_total / (1024 * 1024),
            vram_used_mb=vram_used / (1024 * 1024),
            vram_available_mb=vram_available / (1024 * 1024),
            vram_usage_percent=vram_usage_percent,
            dram_total_mb=dram_info.total / (1024 * 1024),
            dram_used_mb=dram_info.used / (1024 * 1024),
            dram_available_mb=dram_info.available / (1024 * 1024),
            dram_usage_percent=dram_info.percent
        )

def calculate_optimal_blockswap_config(
    model_size_mb: float = 0,
    num_layers: int = 24,
    vram_threshold: float = 50.0,
    auto_hardware_tuning: bool = True
) -> Dict[str, Any]:
    """
    计算最优 BlockSwap 配置
    基于实际模型大小和 VRAM 使用情况
    """
    
    # 获取内存状态
    if torch.cuda.is_available():
        vram_total = torch.cuda.get_device_properties(0).total_memory / (1024 * 1024)
        vram_used = torch.cuda.memory_allocated() / (1024 * 1024)
        props = torch.cuda.get_device_properties(0)
        sm_count = props.multi_processor_count
        gpu_name = props.name
    else:
        vram_total = vram_used = 0
        sm_count = 0
        gpu_name = "CPU"

    # DRAM 信息
    dram_info = psutil.virtual_memory()
    dram_total_mb = dram_info.total / (1024 * 1024)
    dram_available_mb = dram_info.available / (1024 * 1024)
    dram_usage_percent = dram_info.percent

    # 1. 平均层大小
    avg_layer_size_mb = model_size_mb / max(1, num_layers) if model_size_mb > 0 else 100

    # 2. VRAM 阈值计算
    vram_threshold_mb = vram_total * (vram_threshold / 100)
    current_usage_mb = vram_used

    # 实际可用 VRAM = 总 VRAM - 当前使用 - 安全预留(10%)
    safety_reserve_mb = vram_total * 0.1
    actual_available_vram_mb = vram_total - current_usage_mb - safety_reserve_mb

    # 3. 可用 DRAM (带安全边际)
    safe_dram_ratio = 0.8  # 只使用 80% 的可用 DRAM
    usable_dram_mb = dram_available_mb * safe_dram_ratio

    # 4. 总可用内存
    total_available_memory_mb = actual_available_vram_mb + usable_dram_mb

    log.info(f"VRAM-DRAM 平衡分析:")
    log.info(f"   GPU: {gpu_name}")
    log.info(f"   VRAM 总量: {vram_total:.1f}MB")
    log.info(f"   VRAM 已用: {current_usage_mb:.1f}MB")
    log.info(f"   VRAM 可用: {actual_available_vram_mb:.1f}MB (预留 10% 安全边际)")
    log.info(f"   VRAM 阈值: {vram_threshold_mb:.1f}MB ({vram_threshold}%)")
    log.info(f"   DRAM 可用: {dram_available_mb:.1f}MB (使用率 {dram_usage_percent:.1f}%)")
    log.info(f"   DRAM 可用: {usable_dram_mb:.1f}MB (安全使用 80%)")
    log.info(f"   总可用: {total_available_memory_mb:.1f}MB")

    # 5. 智能分块计算
    if model_size_mb > 0:
        if model_size_mb > total_available_memory_mb:
            # 内存完全不足
            log.error(f"内存严重不足！需要 {model_size_mb:.1f}MB，但只有 {total_available_memory_mb:.1f}MB")
            blocks_to_swap = min(num_layers, max(num_layers // 2, int((model_size_mb - total_available_memory_mb) / avg_layer_size_mb) + 5))

        elif model_size_mb > actual_available_vram_mb:
            # VRAM 不足，需要使用 DRAM
            overflow_mb = model_size_mb - actual_available_vram_mb

            if overflow_mb <= usable_dram_mb:
                # DRAM 充足，计算最优分块
                blocks_to_swap = min(num_layers, max(1, int(overflow_mb / avg_layer_size_mb) + 1))
                log.info(f"VRAM 不足 {overflow_mb:.1f}MB，将使用 DRAM，建议交换 {blocks_to_swap} 个块")
            else:
                # DRAM 也不足，需要更多分块
                blocks_to_swap = min(num_layers, max(3, int(overflow_mb / avg_layer_size_mb) + 2))
                log.warning(f"VRAM+DRAM 都紧张，建议交换 {blocks_to_swap} 个块")
        else:
            # 内存充足
            blocks_to_swap = 0
            log.info(f"内存充足，无需 BlockSwap")
    else:
        # 没有模型大小信息，使用保守估计
        blocks_to_swap = 0

    # 6. 计算 CUDA 流数量
    if torch.cuda.is_available() and auto_hardware_tuning:
        if blocks_to_swap > 0:
            # 有 BlockSwap，需要更多流来处理迁移
            num_streams = min(16, max(4, min(blocks_to_swap * 2, sm_count // 4)))
        else:
            # 无 BlockSwap，标准流配置
            num_streams = min(8, max(2, sm_count // 8))
            
        # 根据 GPU 型号自动调整
        if sm_count >= 100:  # RTX 5090/4090 等高端卡
            auto_streams = min(16, max(8, sm_count // 10))
            auto_bandwidth = min(0.9, max(0.7, (100 - vram_threshold) / 100))
        elif sm_count >= 80:  # RTX 3090 等
            auto_streams = min(12, max(6, sm_count // 12))
            auto_bandwidth = min(0.8, max(0.6, (100 - vram_threshold) / 100))
        else:  # 其他 GPU
            auto_streams = min(8, max(4, sm_count // 15))
            auto_bandwidth = min(0.7, max(0.5, (100 - vram_threshold) / 100))
            
        num_streams = auto_streams
        bandwidth_target = auto_bandwidth
    else:
        num_streams = 4
        bandwidth_target = 0.8

    # 7. 计算内存使用比例
    if vram_total > 0:
        memory_ratio = min(0.95, max(0.6, actual_available_vram_mb / vram_total))
    else:
        memory_ratio = 0.8

    config = {
        "blocks_to_swap": blocks_to_swap,
        "num_cuda_streams": num_streams,
        "bandwidth_target": bandwidth_target,
        "vram_threshold_percent": vram_threshold,
        "enable_cuda_optimization": True,
        "enable_dram_optimization": True,
        "memory_analysis": {
            "vram_total_mb": vram_total,
            "vram_used_mb": current_usage_mb,
            "vram_available_mb": actual_available_vram_mb,
            "vram_threshold_mb": vram_threshold_mb,
            "dram_total_mb": dram_total_mb,
            "dram_available_mb": dram_available_mb,
            "dram_usable_mb": usable_dram_mb,
            "dram_usage_percent": dram_usage_percent,
            "total_available_mb": total_available_memory_mb,
            "overflow_mb": max(0, model_size_mb - actual_available_vram_mb) if model_size_mb > 0 else 0,
            "memory_sufficient": model_size_mb <= total_available_memory_mb if model_size_mb > 0 else True,
            "vram_sufficient": model_size_mb <= actual_available_vram_mb if model_size_mb > 0 else True,
        }
    }

    log.info(f"VRAM-DRAM 平衡计算完成:")
    log.info(f"   VRAM: {current_usage_mb:.1f}/{vram_total:.1f}MB ({(current_usage_mb/vram_total*100) if vram_total > 0 else 0:.1f}%)")
    log.info(f"   DRAM: {dram_available_mb:.1f}/{dram_total_mb:.1f}MB (使用率 {dram_usage_percent:.1f}%)")
    log.info(f"   总可用: {total_available_memory_mb:.1f}MB (VRAM{actual_available_vram_mb:.1f}MB + DRAM{usable_dram_mb:.1f}MB)")
    log.info(f"   配置: blocks_to_swap={blocks_to_swap}, streams={num_streams}, ratio={memory_ratio:.0%}")

    return config

# 全局管理器实例
_global_manager: Optional[IntelligentVRAMManager] = None
_manager_lock = threading.Lock()

def get_vram_manager(threshold_percent: float = 50.0) -> IntelligentVRAMManager:
    """获取全局 VRAM 管理器实例"""
    global _global_manager

    with _manager_lock:
        if _global_manager is None:
            _global_manager = IntelligentVRAMManager(threshold_percent)
        elif _global_manager.vram_threshold_percent != threshold_percent:
            _global_manager.vram_threshold_percent = threshold_percent
            log.info(f"更新 VRAM 阈值: {threshold_percent}%")

        return _global_manager
