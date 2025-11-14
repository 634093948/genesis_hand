# 智能 VRAM 管理系统集成指南

## 概述

基于 IntelligentVRAMNode 的智能显存管理系统已集成到 Genesis Hand 项目中。

---

## ✅ 已完成的工作

### 1. 创建智能 VRAM 管理器 ✅

**文件**: `genesis/apps/intelligent_vram_manager.py`

**功能**:
- VRAM-DRAM 平衡计算
- 自动硬件检测和配置
- 智能分块计算
- 内存统计和监控

### 2. 更新 Gradio UI ✅

**文件**: `genesis/apps/wanvideo_gradio_app.py`

**新增参数**:
```python
# 主开关
block_swap_enabled = "启用智能 VRAM 管理"

# 自动调优
auto_hardware_tuning = "自动硬件调优" (默认: True)
vram_threshold_percent = "VRAM 使用阈值" (默认: 50%)

# 高级参数
blocks_to_swap = "手动分块数" (0-40, 默认: 0=自动)
enable_cuda_optimization = "启用 CUDA 优化" (默认: True)
enable_dram_optimization = "启用 DRAM 优化" (默认: True)
num_cuda_streams = "CUDA 流数量" (1-16, 默认: 8)
bandwidth_target = "带宽目标" (0.1-1.0, 默认: 0.8)
offload_txt_emb = "卸载文本嵌入" (默认: False)
offload_img_emb = "卸载图像嵌入" (默认: False)
vace_blocks_to_swap = "VAE 分块数" (0-15, 默认: 0)
vram_debug_mode = "调试模式" (默认: False)
```

---

## 📋 需要完成的集成步骤

### 步骤 1: 更新函数签名

在 `generate_video()` 函数中添加新参数：

```python
def generate_video(
    self,
    # ... 现有参数 ...
    # Optimization parameters
    compile_enabled: bool,
    compile_backend: str,
    block_swap_enabled: bool,
    # 新增: 智能 VRAM 管理参数
    auto_hardware_tuning: bool = True,
    vram_threshold_percent: float = 50.0,
    blocks_to_swap: int = 0,
    enable_cuda_optimization: bool = True,
    enable_dram_optimization: bool = True,
    num_cuda_streams: int = 8,
    bandwidth_target: float = 0.8,
    offload_txt_emb: bool = False,
    offload_img_emb: bool = False,
    vace_blocks_to_swap: int = 0,
    vram_debug_mode: bool = False,
    # ... 其他参数 ...
):
```

### 步骤 2: 使用智能 VRAM 管理器

在 `generate_video()` 中替换原有的 block swap 逻辑：

```python
# 原有代码 (删除):
block_swap_args = None
if block_swap_enabled and self.block_swap:
    try:
        swap_result = self.block_swap.prepare(
            blocks_to_swap=blocks_to_swap,
            # ...
        )
        block_swap_args = swap_result[0] if swap_result else None
    except:
        block_swap_args = None

# 新代码 (替换为):
from .intelligent_vram_manager import calculate_optimal_blockswap_config, get_vram_manager

block_swap_args = None
if block_swap_enabled:
    try:
        # 获取 VRAM 管理器
        vram_manager = get_vram_manager(vram_threshold_percent)
        
        # 获取内存统计
        stats = vram_manager.get_memory_stats()
        
        if vram_debug_mode:
            print(f"[VRAM] 当前状态:")
            print(f"  VRAM: {stats.vram_used_mb:.1f}/{stats.vram_total_mb:.1f}MB ({stats.vram_usage_percent:.1f}%)")
            print(f"  DRAM: {stats.dram_used_mb:.1f}/{stats.dram_total_mb:.1f}MB ({stats.dram_usage_percent:.1f}%)")
        
        # 计算最优配置
        if auto_hardware_tuning:
            # 自动模式: 根据模型大小和硬件自动计算
            # 注意: 这里需要模型大小信息，可以在模型加载后获取
            optimal_config = calculate_optimal_blockswap_config(
                model_size_mb=0,  # TODO: 从加载的模型获取实际大小
                num_layers=24,  # TODO: 从模型配置获取
                vram_threshold=vram_threshold_percent,
                auto_hardware_tuning=True
            )
            
            # 使用自动计算的参数
            block_swap_args = {
                "blocks_to_swap": optimal_config["blocks_to_swap"],
                "num_cuda_streams": optimal_config["num_cuda_streams"],
                "bandwidth_target": optimal_config["bandwidth_target"],
                "enable_cuda_optimization": enable_cuda_optimization,
                "enable_dram_optimization": enable_dram_optimization,
                "vram_threshold_percent": vram_threshold_percent,
                "offload_txt_emb": offload_txt_emb,
                "offload_img_emb": offload_img_emb,
                "vace_blocks_to_swap": vace_blocks_to_swap,
            }
            
            if vram_debug_mode:
                print(f"[VRAM] 自动配置:")
                print(f"  分块数: {optimal_config['blocks_to_swap']}")
                print(f"  CUDA 流: {optimal_config['num_cuda_streams']}")
                print(f"  带宽目标: {optimal_config['bandwidth_target']:.0%}")
        else:
            # 手动模式: 使用用户指定的参数
            block_swap_args = {
                "blocks_to_swap": blocks_to_swap,
                "num_cuda_streams": num_cuda_streams,
                "bandwidth_target": bandwidth_target,
                "enable_cuda_optimization": enable_cuda_optimization,
                "enable_dram_optimization": enable_dram_optimization,
                "vram_threshold_percent": vram_threshold_percent,
                "offload_txt_emb": offload_txt_emb,
                "offload_img_emb": offload_img_emb,
                "vace_blocks_to_swap": vace_blocks_to_swap,
            }
            
            if vram_debug_mode:
                print(f"[VRAM] 手动配置:")
                print(f"  分块数: {blocks_to_swap}")
                print(f"  CUDA 流: {num_cuda_streams}")
                print(f"  带宽目标: {bandwidth_target:.0%}")
        
        print(f"✓ 智能 VRAM 管理已启用")
        
    except Exception as e:
        print(f"[ERROR] 智能 VRAM 管理初始化失败: {e}")
        if vram_debug_mode:
            import traceback
            traceback.print_exc()
        block_swap_args = None
```

### 步骤 3: 更新 Gradio 输入

在 UI 的 `generate_button.click()` 中添加新参数：

```python
generate_button.click(
    fn=generate_wrapper,
    inputs=[
        # ... 现有输入 ...
        compile_enabled,
        compile_backend,
        block_swap_enabled,
        # 新增输入
        auto_hardware_tuning,
        vram_threshold_percent,
        blocks_to_swap,
        enable_cuda_optimization,
        enable_dram_optimization,
        num_cuda_streams,
        bandwidth_target,
        offload_txt_emb,
        offload_img_emb,
        vace_blocks_to_swap,
        vram_debug_mode,
        # ... 其他输入 ...
    ],
    outputs=[video_output, frames_gallery, metadata_output]
)
```

### 步骤 4: 更新预设配置

修改 `apply_preset()` 函数以包含新参数：

```python
def apply_preset(preset_name):
    if "Fast Preview" in preset_name:
        return (4, 1.0, 5.0, "sa_ode_stable/lowstep", 
                False, False, True, 50.0)  # 新增: auto_tuning, threshold
    elif "Standard" in preset_name:
        return (30, 6.0, 5.0, "unipc", 
                False, False, True, 50.0)
    elif "High Quality" in preset_name:
        return (50, 8.0, 5.0, "ddim", 
                False, False, True, 50.0)
    elif "Memory Optimized" in preset_name:
        return (30, 6.0, 5.0, "unipc", 
                False, True, True, 40.0)  # 降低阈值，更激进的内存管理
    elif "Speed Optimized" in preset_name:
        return (30, 6.0, 5.0, "unipc", 
                True, False, True, 60.0)  # 提高阈值，减少迁移
    else:
        return (30, 6.0, 5.0, "unipc", 
                False, False, True, 50.0)

preset_buttons.change(
    apply_preset,
    inputs=[preset_buttons],
    outputs=[
        steps, cfg, shift, scheduler, 
        compile_enabled, block_swap_enabled,
        auto_hardware_tuning, vram_threshold_percent  # 新增输出
    ]
)
```

---

## 🎯 核心算法

### VRAM-DRAM 平衡计算

```python
# 1. 获取内存状态
vram_total_mb = GPU 总显存
vram_used_mb = 当前使用的显存
actual_available_vram_mb = vram_total - vram_used - safety_reserve(10%)

dram_available_mb = 系统可用内存
usable_dram_mb = dram_available * 0.8  # 安全使用 80%

# 2. 计算溢出量
overflow_mb = model_size_mb - actual_available_vram_mb

# 3. 智能分块
if overflow_mb > 0:
    blocks_to_swap = int(overflow_mb / avg_layer_size_mb) + 1
else:
    blocks_to_swap = 0  # 内存充足，无需交换

# 4. 硬件自适应
if GPU == RTX 5090/4090:
    num_streams = 16
    bandwidth = 0.9
elif GPU == RTX 3090:
    num_streams = 12
    bandwidth = 0.8
else:
    num_streams = 8
    bandwidth = 0.7
```

---

## 📊 参数说明

### 自动调优模式（推荐）

```
启用智能 VRAM 管理: ✓
自动硬件调优: ✓
VRAM 阈值: 50%
```

**效果**:
- 自动检测 GPU 型号
- 自动计算最优分块数
- 自动配置 CUDA 流数量
- 自动调整带宽目标

### 手动模式（高级用户）

```
启用智能 VRAM 管理: ✓
自动硬件调优: ✗
手动分块数: 8
CUDA 流数量: 12
带宽目标: 0.8
```

**适用场景**:
- 需要精确控制内存使用
- 特殊硬件配置
- 性能调优

---

## 🔍 调试模式

启用调试模式后，会输出详细日志：

```
[VRAM] 当前状态:
  VRAM: 2048.0/32606.6MB (6.3%)
  DRAM: 26123.4/65379.6MB (39.9%)

[VRAM] VRAM-DRAM 平衡分析:
  GPU: NVIDIA GeForce RTX 5090
  VRAM 总量: 32606.6MB
  VRAM 已用: 2048.0MB
  VRAM 可用: 27332.9MB (预留 10% 安全边际)
  VRAM 阈值: 16303.3MB (50%)
  DRAM 可用: 39256.2MB (使用率 39.9%)
  总可用: 66589.1MB

[VRAM] 自动配置:
  分块数: 0
  CUDA 流: 16
  带宽目标: 90%

✓ 智能 VRAM 管理已启用
```

---

## ⚠️ 注意事项

### 1. 模型大小获取

当前实现中，`model_size_mb` 设置为 0（自动模式）。理想情况下应该：

```python
# 在模型加载后获取实际大小
if hasattr(model, 'model'):
    model_params = sum(p.numel() for p in model.model.parameters())
    model_size_mb = model_params * 4 / (1024 * 1024)  # FP32
else:
    model_size_mb = 0
```

### 2. 层数获取

```python
# 从模型配置获取层数
if hasattr(model, 'config') and hasattr(model.config, 'num_hidden_layers'):
    num_layers = model.config.num_hidden_layers
else:
    num_layers = 24  # 默认值
```

### 3. 与现有 BlockSwap 节点的兼容性

如果项目中已有 `WanVideoBlockSwap` 节点，可以选择：
- **方案 A**: 完全替换为智能 VRAM 管理器
- **方案 B**: 保留两者，让用户选择使用哪个

---

## ✅ 测试清单

- [ ] UI 参数正确显示
- [ ] 自动调优模式工作正常
- [ ] 手动模式参数生效
- [ ] VRAM 统计正确
- [ ] 调试日志输出正常
- [ ] 预设配置正确应用
- [ ] 生成过程无错误

---

## 📚 相关文件

1. **intelligent_vram_manager.py** - 核心管理器
2. **wanvideo_gradio_app.py** - UI 和集成
3. **IntelligentVRAMNode/** - 原始参考实现

---

**下一步**: 按照上述步骤完成集成，然后测试智能 VRAM 管理功能。
