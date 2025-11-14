#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 ComfyUI 链接模型到 Genesis Hand
使用 mklink 创建符号链接，避免重复下载
"""

import os
import sys
from pathlib import Path
import subprocess

def find_comfyui_models():
    """查找所有可能的 ComfyUI 模型目录"""
    possible_paths = [
        # 从 twodog 配置中找到的路径
        Path("E:/liliyuanshangmie/mao/comfyui-CAT优化版-20251105/ComfyUI/models"),
        Path("E:/liliyuanshangmie/Fuxkcomfy_lris_kernel_gen2-4_speed_safe/FuxkComfy/models"),
        Path("D:/liliyuanshangmie/Fuxkcomfy_lris_kernel_gen2-4_speed_safe/FuxkComfy/models"),
        Path("D:/liliyuanshangmie/fuxkcomfy_windows_portable/FuxkComfy/models"),
        # 其他常见位置
        Path("C:/ComfyUI/models"),
        Path("E:/ComfyUI/models"),
        Path("D:/ComfyUI/models"),
    ]
    
    found = []
    for path in possible_paths:
        if path.exists():
            # 检查是否有实际的模型文件
            has_models = False
            for subdir in path.iterdir():
                if subdir.is_dir() and list(subdir.glob("*.*")):
                    has_models = True
                    break
            if has_models:
                found.append(path)
    
    return found

def create_junction(source, target):
    """创建目录连接（Windows mklink /J）"""
    try:
        # 确保目标父目录存在
        target.parent.mkdir(parents=True, exist_ok=True)
        
        # 如果目标已存在，先删除
        if target.exists():
            if target.is_symlink() or target.is_junction():
                target.unlink()
            else:
                print(f"  ⚠️  目标已存在且不是链接: {target}")
                return False
        
        # 创建目录连接
        cmd = f'mklink /J "{target}" "{source}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True
        else:
            print(f"  ❌ 创建链接失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return False

def scan_models_in_directory(models_dir):
    """扫描目录中的模型"""
    models = {}
    
    # InfiniteTalk 需要的模型类型
    model_types = {
        "wanvideo": ["*.gguf", "*.safetensors", "*.bin"],
        "wav2vec2": ["*.safetensors", "*.bin"],
        "clip_vision": ["*.safetensors", "*.bin"],
    }
    
    for model_type, patterns in model_types.items():
        type_dir = models_dir / model_type
        if not type_dir.exists():
            continue
        
        files = []
        for pattern in patterns:
            files.extend(type_dir.glob(pattern))
            # 也检查子目录
            files.extend(type_dir.glob(f"*/{pattern}"))
            files.extend(type_dir.glob(f"*/*/{pattern}"))
        
        if files:
            models[model_type] = {
                "path": type_dir,
                "files": [f.relative_to(type_dir) for f in files]
            }
    
    return models

def main():
    print("=" * 70)
    print("从 ComfyUI 链接模型到 Genesis Hand")
    print("=" * 70)
    
    # 查找 ComfyUI 模型目录
    print("\n1. 搜索 ComfyUI 模型目录...")
    comfyui_models_dirs = find_comfyui_models()
    
    if not comfyui_models_dirs:
        print("   ❌ 未找到任何 ComfyUI 模型目录")
        print("\n可能的原因:")
        print("  1. ComfyUI 未安装或路径不在预期位置")
        print("  2. 模型目录为空")
        print("\n请手动指定 ComfyUI 模型目录，或使用 download_models.py 下载模型")
        return
    
    print(f"   ✅ 找到 {len(comfyui_models_dirs)} 个 ComfyUI 模型目录:")
    for i, path in enumerate(comfyui_models_dirs, 1):
        print(f"      [{i}] {path}")
    
    # 扫描每个目录中的模型
    print("\n2. 扫描模型文件...")
    all_models = {}
    for models_dir in comfyui_models_dirs:
        models = scan_models_in_directory(models_dir)
        if models:
            all_models[models_dir] = models
    
    if not all_models:
        print("   ❌ 未找到任何 InfiniteTalk 相关模型")
        print("\n需要的模型类型:")
        print("  - wanvideo/*.gguf 或 *.safetensors (主模型)")
        print("  - wav2vec2/*.safetensors (音频模型)")
        print("  - clip_vision/*.safetensors (视觉模型)")
        return
    
    # 显示找到的模型
    print("   ✅ 找到以下模型:")
    for models_dir, models in all_models.items():
        print(f"\n   来自: {models_dir}")
        for model_type, info in models.items():
            print(f"      {model_type}:")
            for file in info["files"][:3]:  # 只显示前3个
                print(f"        - {file}")
            if len(info["files"]) > 3:
                print(f"        ... 还有 {len(info["files"]) - 3} 个文件")
    
    # 选择源目录
    if len(all_models) == 1:
        source_dir = list(all_models.keys())[0]
        print(f"\n3. 使用模型目录: {source_dir}")
    else:
        print("\n3. 选择要链接的模型目录:")
        dirs = list(all_models.keys())
        for i, path in enumerate(dirs, 1):
            model_count = sum(len(m["files"]) for m in all_models[path].values())
            print(f"   [{i}] {path} ({model_count} 个文件)")
        
        try:
            choice = int(input("\n请选择 (1-{}): ".format(len(dirs))))
            if 1 <= choice <= len(dirs):
                source_dir = dirs[choice - 1]
            else:
                print("无效选择")
                return
        except ValueError:
            print("无效输入")
            return
    
    # 目标目录
    target_base = Path("models")
    target_base.mkdir(exist_ok=True)
    
    # 创建链接
    print("\n4. 创建目录链接...")
    print("-" * 70)
    
    models = all_models[source_dir]
    success_count = 0
    fail_count = 0
    
    for model_type, info in models.items():
        source = info["path"]
        target = target_base / model_type
        
        print(f"\n  {model_type}:")
        print(f"    源: {source}")
        print(f"    目标: {target}")
        
        if create_junction(source, target):
            print(f"    ✅ 链接创建成功")
            success_count += 1
        else:
            print(f"    ❌ 链接创建失败")
            fail_count += 1
    
    # 总结
    print("\n" + "=" * 70)
    print("总结")
    print("=" * 70)
    print(f"  ✅ 成功: {success_count}")
    print(f"  ❌ 失败: {fail_count}")
    
    if success_count > 0:
        print("\n✅ 模型链接完成！")
        print("\n下一步:")
        print("  1. 运行 python check_infinitetalk_deps.py 验证")
        print("  2. 启动 Gradio UI 测试")
        print("\n注意:")
        print("  - 链接的模型不会占用额外磁盘空间")
        print("  - 修改链接目录中的文件会影响原始 ComfyUI 模型")
        print("  - 如果需要删除链接，使用: rmdir models\\<model_type>")
    
    if fail_count > 0:
        print("\n⚠️  部分链接创建失败")
        print("  可能需要管理员权限")
        print("  请以管理员身份运行此脚本")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户取消")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
