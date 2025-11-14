#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查并链接 ComfyUI 中的模型到 Genesis Hand 项目
"""

import os
import shutil
from pathlib import Path

def find_comfyui_models():
    """查找 ComfyUI 模型目录"""
    possible_paths = [
        Path("C:/ComfyUI/models"),
        Path("C:/Users") / os.environ.get("USERNAME", "") / "ComfyUI/models",
        Path.home() / "ComfyUI/models",
        Path("D:/ComfyUI/models"),
        Path("E:/ComfyUI/models"),
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    return None

def check_model_file(model_path, model_name):
    """检查模型文件是否存在"""
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        return True, f"存在 ({size_mb:.1f} MB)"
    return False, "不存在"

def main():
    print("=" * 70)
    print("InfiniteTalk 模型检查和链接工具")
    print("=" * 70)
    
    # 查找 ComfyUI 模型目录
    print("\n1. 查找 ComfyUI 模型目录...")
    comfyui_models = find_comfyui_models()
    
    if comfyui_models:
        print(f"   ✅ 找到 ComfyUI 模型目录: {comfyui_models}")
    else:
        print("   ⚠️  未找到 ComfyUI 模型目录")
        print("   请手动指定 ComfyUI 安装路径")
        return
    
    # 定义需要的模型
    models_needed = {
        "WanVideo 主模型": {
            "comfyui_path": comfyui_models / "wanvideo",
            "genesis_path": Path("models/wanvideo"),
            "files": [
                "wan2.1-i2v-14b-480p-Q8_0.gguf",
                "Wan2_1_VAE_bf16.safetensors",
            ]
        },
        "Wav2Vec 模型": {
            "comfyui_path": comfyui_models / "wav2vec2",
            "genesis_path": Path("models/wav2vec2"),
            "files": [
                "wav2vec2-chinese-base_fp16.safetensors",
                "chinese-wav2vec2-base.safetensors",
            ]
        },
        "CLIP Vision 模型": {
            "comfyui_path": comfyui_models / "clip_vision",
            "genesis_path": Path("models/clip_vision"),
            "files": [
                "clip_vision_h.safetensors",
            ]
        },
        "MultiTalk 模型": {
            "comfyui_path": comfyui_models / "wanvideo" / "InfiniteTalk",
            "genesis_path": Path("models/wanvideo/InfiniteTalk"),
            "files": [
                "multitalk_model.safetensors",
            ]
        }
    }
    
    print("\n2. 检查模型文件...")
    print("-" * 70)
    
    found_models = {}
    missing_models = {}
    
    for category, info in models_needed.items():
        print(f"\n  {category}:")
        comfyui_dir = info["comfyui_path"]
        
        if not comfyui_dir.exists():
            print(f"    ⚠️  ComfyUI 目录不存在: {comfyui_dir}")
            missing_models[category] = info
            continue
        
        found_files = []
        for model_file in info["files"]:
            model_path = comfyui_dir / model_file
            exists, status = check_model_file(model_path, model_file)
            
            if exists:
                print(f"    ✅ {model_file} - {status}")
                found_files.append(model_path)
            else:
                print(f"    ❌ {model_file} - {status}")
        
        if found_files:
            found_models[category] = {
                "files": found_files,
                "genesis_path": info["genesis_path"]
            }
    
    # 创建链接或复制
    if found_models:
        print("\n3. 创建模型链接...")
        print("-" * 70)
        
        for category, info in found_models.items():
            print(f"\n  {category}:")
            genesis_dir = info["genesis_path"]
            
            # 创建目标目录
            genesis_dir.mkdir(parents=True, exist_ok=True)
            
            for source_file in info["files"]:
                target_file = genesis_dir / source_file.name
                
                if target_file.exists():
                    print(f"    ⏭️  {source_file.name} - 已存在，跳过")
                    continue
                
                try:
                    # 尝试创建符号链接（Windows 需要管理员权限）
                    try:
                        os.symlink(source_file, target_file)
                        print(f"    ✅ {source_file.name} - 符号链接已创建")
                    except OSError:
                        # 如果无法创建符号链接，则复制文件
                        shutil.copy2(source_file, target_file)
                        print(f"    ✅ {source_file.name} - 文件已复制")
                except Exception as e:
                    print(f"    ❌ {source_file.name} - 失败: {e}")
    
    # 总结
    print("\n" + "=" * 70)
    print("总结")
    print("=" * 70)
    
    if found_models:
        print(f"\n✅ 找到 {len(found_models)} 类模型")
        for category in found_models.keys():
            print(f"   - {category}")
    
    if missing_models:
        print(f"\n⚠️  缺少 {len(missing_models)} 类模型")
        for category in missing_models.keys():
            print(f"   - {category}")
    
    print("\n注意事项:")
    print("  1. 如果无法创建符号链接，文件会被复制（占用额外空间）")
    print("  2. 某些模型可能在 ComfyUI 的不同位置")
    print("  3. 可以手动复制模型文件到对应目录")
    print("  4. InfiniteTalk 无音频模式不需要 Wav2Vec 模型")

if __name__ == "__main__":
    main()
