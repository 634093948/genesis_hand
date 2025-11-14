#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InfiniteTalk 依赖检查脚本
检查所有必需的 Python 包和模型文件
"""

import sys
import os
import importlib.util

def check_package(package_name, import_name=None):
    """检查 Python 包是否已安装"""
    if import_name is None:
        import_name = package_name
    
    try:
        spec = importlib.util.find_spec(import_name)
        if spec is not None:
            return True, "已安装"
        else:
            return False, "未安装"
    except (ImportError, ModuleNotFoundError):
        return False, "未安装"
    except Exception as e:
        return False, f"检查失败: {e}"

def check_file(filepath):
    """检查文件是否存在"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        return True, f"存在 ({size / 1024 / 1024:.1f} MB)"
    else:
        return False, "不存在"

def main():
    print("=" * 70)
    print("InfiniteTalk 依赖检查")
    print("=" * 70)
    
    # 核心依赖（requirements.txt）
    core_deps = [
        ("ftfy", "ftfy"),
        ("accelerate", "accelerate"),
        ("einops", "einops"),
        ("diffusers", "diffusers"),
        ("peft", "peft"),
        ("sentencepiece", "sentencepiece"),
        ("protobuf", "google.protobuf"),
        ("pyloudnorm", "pyloudnorm"),
        ("gguf", "gguf"),
        ("opencv-python", "cv2"),
        ("scipy", "scipy"),
    ]
    
    # InfiniteTalk 特定依赖
    infinitetalk_deps = [
        ("torch", "torch"),
        ("torchaudio", "torchaudio"),
        ("transformers", "transformers"),
        ("numpy", "numpy"),
        ("PIL/Pillow", "PIL"),
        ("color-matcher", "color_matcher"),
    ]
    
    # Gradio 相关
    gradio_deps = [
        ("gradio", "gradio"),
        ("fastapi", "fastapi"),
    ]
    
    print("\n1. 核心依赖 (requirements.txt)")
    print("-" * 70)
    missing_core = []
    for package, import_name in core_deps:
        installed, status = check_package(package, import_name)
        symbol = "✅" if installed else "❌"
        print(f"  {symbol} {package:20s} - {status}")
        if not installed:
            missing_core.append(package)
    
    print("\n2. InfiniteTalk 特定依赖")
    print("-" * 70)
    missing_infinitetalk = []
    for package, import_name in infinitetalk_deps:
        installed, status = check_package(package, import_name)
        symbol = "✅" if installed else "❌"
        print(f"  {symbol} {package:20s} - {status}")
        if not installed:
            missing_infinitetalk.append(package)
    
    print("\n3. Gradio UI 依赖")
    print("-" * 70)
    missing_gradio = []
    for package, import_name in gradio_deps:
        installed, status = check_package(package, import_name)
        symbol = "✅" if installed else "❌"
        print(f"  {symbol} {package:20s} - {status}")
        if not installed:
            missing_gradio.append(package)
    
    print("\n4. 模型文件检查")
    print("-" * 70)
    
    # Wav2Vec 模型
    wav2vec_dir = "models/wav2vec2/"
    if os.path.exists(wav2vec_dir):
        files = [f for f in os.listdir(wav2vec_dir) 
                if f.endswith(('.safetensors', '.bin'))]
        if files:
            print(f"  ✅ Wav2Vec 模型: {len(files)} 个文件")
            for f in files[:3]:  # 只显示前3个
                print(f"     - {f}")
            if len(files) > 3:
                print(f"     ... 还有 {len(files) - 3} 个文件")
        else:
            print(f"  ⚠️  Wav2Vec 模型目录存在但为空")
    else:
        print(f"  ⚠️  Wav2Vec 模型目录不存在: {wav2vec_dir}")
    
    # 静音嵌入
    silence_path = "genesis/custom_nodes/Comfyui/ComfyUI-WanVideoWrapper/multitalk/encoded_silence.safetensors"
    exists, status = check_file(silence_path)
    symbol = "✅" if exists else "⚠️"
    print(f"  {symbol} encoded_silence.safetensors - {status}")
    
    # Wav2Vec 配置
    config_path = "genesis/custom_nodes/Comfyui/ComfyUI-WanVideoWrapper/multitalk/wav2vec2_config.json"
    exists, status = check_file(config_path)
    symbol = "✅" if exists else "❌"
    print(f"  {symbol} wav2vec2_config.json - {status}")
    
    print("\n" + "=" * 70)
    print("总结")
    print("=" * 70)
    
    all_missing = missing_core + missing_infinitetalk + missing_gradio
    
    if not all_missing:
        print("✅ 所有 Python 依赖都已安装！")
    else:
        print(f"❌ 缺少 {len(all_missing)} 个依赖包:")
        for pkg in all_missing:
            print(f"   - {pkg}")
        
        print("\n安装命令:")
        print(f"pip install {' '.join(all_missing)}")
    
    print("\n注意事项:")
    print("  1. Wav2Vec 模型需要手动下载到 models/wav2vec2/")
    print("  2. encoded_silence.safetensors 通常随 ComfyUI-WanVideoWrapper 提供")
    print("  3. 如果不使用音频，可以跳过 Wav2Vec 模型")
    print("  4. color-matcher 用于颜色匹配，可以设置 colormatch='disabled' 禁用")
    
    return len(all_missing) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
