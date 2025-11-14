#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InfiniteTalk 模型自动下载脚本
"""

import os
import sys
from pathlib import Path

def check_huggingface_cli():
    """检查 huggingface-cli 是否已安装"""
    try:
        import huggingface_hub
        return True
    except ImportError:
        return False

def install_huggingface_cli():
    """安装 huggingface-hub"""
    print("正在安装 huggingface-hub...")
    os.system("pip install huggingface-hub")

def download_model(repo_id, filename, local_dir, description):
    """下载单个模型文件"""
    print(f"\n下载 {description}...")
    print(f"  仓库: {repo_id}")
    print(f"  文件: {filename}")
    print(f"  目标: {local_dir}")
    
    # 创建目录
    Path(local_dir).mkdir(parents=True, exist_ok=True)
    
    # 检查文件是否已存在
    target_file = Path(local_dir) / filename
    if target_file.exists():
        size_mb = target_file.stat().st_size / (1024 * 1024)
        print(f"  ⏭️  文件已存在 ({size_mb:.1f} MB)，跳过")
        return True
    
    # 下载
    try:
        from huggingface_hub import hf_hub_download
        print("  ⏬ 开始下载...")
        hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=local_dir,
            local_dir_use_symlinks=False
        )
        print("  ✅ 下载完成")
        return True
    except Exception as e:
        print(f"  ❌ 下载失败: {e}")
        return False

def main():
    print("=" * 70)
    print("InfiniteTalk 模型下载工具")
    print("=" * 70)
    
    # 检查 huggingface-hub
    print("\n1. 检查依赖...")
    if not check_huggingface_cli():
        print("   ⚠️  huggingface-hub 未安装")
        response = input("   是否安装? (y/n): ")
        if response.lower() == 'y':
            install_huggingface_cli()
        else:
            print("   ❌ 无法继续，需要 huggingface-hub")
            return
    else:
        print("   ✅ huggingface-hub 已安装")
    
    # 定义模型
    models = {
        "1": {
            "name": "WanVideo 主模型 (GGUF Q8_0, ~10 GB)",
            "repo_id": "city96/Wan2.1-I2V-14B-480P-gguf",
            "filename": "wan2.1-i2v-14b-480p-Q8_0.gguf",
            "local_dir": "models/wanvideo",
            "required": True
        },
        "2": {
            "name": "VAE 模型 (BF16, ~300 MB)",
            "repo_id": "Kijai/WanVideo_comfy",
            "filename": "Wan2_1_VAE_bf16.safetensors",
            "local_dir": "models/wanvideo",
            "required": True
        },
        "3": {
            "name": "MultiTalk 模型 (GGUF, ~2 GB)",
            "repo_id": "Kijai/WanVideo_comfy_GGUF",
            "filename": "InfiniteTalk/multitalk_model.safetensors",
            "local_dir": "models/wanvideo",
            "required": True
        },
        "4": {
            "name": "CLIP Vision (可选, ~3.7 GB)",
            "repo_id": "h94/IP-Adapter",
            "filename": "models/image_encoder/model.safetensors",
            "local_dir": "models/clip_vision",
            "required": False
        },
        "5": {
            "name": "Wav2Vec 中文模型 (可选, ~300 MB)",
            "repo_id": "TencentGameMate/chinese-wav2vec2-base",
            "filename": "pytorch_model.bin",
            "local_dir": "models/wav2vec2",
            "required": False
        }
    }
    
    # 显示模型列表
    print("\n2. 可下载的模型:")
    print("-" * 70)
    for key, model in models.items():
        status = "必需" if model["required"] else "可选"
        print(f"  [{key}] {model['name']} - {status}")
    
    print("\n3. 选择下载模式:")
    print("  [a] 下载所有必需模型 (~12 GB)")
    print("  [b] 下载所有模型（包含可选, ~16 GB）")
    print("  [c] 自定义选择")
    print("  [q] 退出")
    
    choice = input("\n请选择: ").lower()
    
    to_download = []
    
    if choice == 'a':
        # 只下载必需模型
        to_download = [k for k, v in models.items() if v["required"]]
    elif choice == 'b':
        # 下载所有模型
        to_download = list(models.keys())
    elif choice == 'c':
        # 自定义选择
        print("\n输入要下载的模型编号（用空格分隔，如: 1 2 3）:")
        selected = input("编号: ").split()
        to_download = [s for s in selected if s in models]
    elif choice == 'q':
        print("退出")
        return
    else:
        print("无效选择")
        return
    
    if not to_download:
        print("没有选择任何模型")
        return
    
    # 确认下载
    print("\n4. 将下载以下模型:")
    print("-" * 70)
    total_size = 0
    size_map = {
        "1": 10000,  # MB
        "2": 300,
        "3": 2000,
        "4": 3700,
        "5": 300
    }
    
    for key in to_download:
        model = models[key]
        size = size_map.get(key, 0)
        total_size += size
        print(f"  - {model['name']}")
    
    print(f"\n总大小约: {total_size / 1024:.1f} GB")
    
    response = input("\n确认下载? (y/n): ")
    if response.lower() != 'y':
        print("取消下载")
        return
    
    # 开始下载
    print("\n5. 开始下载...")
    print("=" * 70)
    
    success_count = 0
    fail_count = 0
    
    for i, key in enumerate(to_download, 1):
        model = models[key]
        print(f"\n[{i}/{len(to_download)}] {model['name']}")
        
        if download_model(
            model["repo_id"],
            model["filename"],
            model["local_dir"],
            model["name"]
        ):
            success_count += 1
        else:
            fail_count += 1
    
    # 总结
    print("\n" + "=" * 70)
    print("下载完成")
    print("=" * 70)
    print(f"  ✅ 成功: {success_count}")
    print(f"  ❌ 失败: {fail_count}")
    
    if fail_count > 0:
        print("\n失败的模型可以:")
        print("  1. 重新运行此脚本")
        print("  2. 手动从 Hugging Face 下载")
        print("  3. 查看 INFINITETALK_MODELS_NEEDED.md 获取下载链接")
    
    if success_count > 0:
        print("\n下一步:")
        print("  1. 运行 python check_infinitetalk_deps.py 验证")
        print("  2. 启动 Gradio UI 测试")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户取消")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
