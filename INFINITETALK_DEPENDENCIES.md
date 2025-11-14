# InfiniteTalk 依赖清单

## 必需的 Python 包

### 1. color-matcher ✅ 已安装
**用途**: 颜色匹配功能，用于视频帧之间的颜色一致性

**安装命令**:
```bash
pip install color-matcher
```

**相关参数**:
- `colormatch`: 控制颜色匹配方法
- 可选值: `'disabled'`, `'mkl'`, `'hm'`, `'reinhard'`, `'mvgd'`, `'hm-mvgd-hm'`, `'hm-mkl-hm'`
- 默认值: `'mkl'`

**如果缺失**:
- 错误: `No module named 'color_matcher'`
- 影响: 采样阶段崩溃（如果 colormatch != 'disabled'）

**解决方案**:
1. 安装包: `pip install color-matcher`
2. 或禁用颜色匹配: 设置 `colormatch='disabled'`

---

### 2. torchaudio ✅ 应该已安装
**用途**: 加载音频文件

**安装命令**:
```bash
pip install torchaudio
```

**如果缺失**:
- 错误: `No module named 'torchaudio'`
- 影响: 无法加载音频文件（带音频模式失败）

---

## 必需的模型文件

### 1. Wav2Vec 模型（仅带音频模式需要）
**位置**: `models/wav2vec2/`

**支持的文件格式**:
- `*.safetensors`
- `*.bin`

**模型类型**: Tencent Wav2Vec2

**如果缺失**:
- 错误: 找不到 Wav2Vec 模型文件
- 影响: 带音频模式失败，但会自动回退到静音模式

**获取方式**:
- 从 Hugging Face 下载
- 或从项目文档获取下载链接

---

### 2. encoded_silence.safetensors
**位置**: `genesis/custom_nodes/Comfyui/ComfyUI-WanVideoWrapper/multitalk/encoded_silence.safetensors`

**用途**: 无音频模式的静音嵌入

**如果缺失**:
- 警告: "No encoded silence file found, padding with end of audio embedding instead."
- 影响: 无音频模式可能使用替代方案（使用音频嵌入末尾填充）

---

## 依赖检查脚本

创建一个简单的检查脚本来验证所有依赖：

```python
import sys
import os

def check_dependencies():
    print("=== InfiniteTalk 依赖检查 ===\n")
    
    # 检查 Python 包
    packages = {
        'color_matcher': 'color-matcher',
        'torchaudio': 'torchaudio',
        'torch': 'torch',
    }
    
    print("1. Python 包检查:")
    for module, package in packages.items():
        try:
            __import__(module)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - 运行: pip install {package}")
    
    print("\n2. 模型文件检查:")
    
    # 检查 Wav2Vec 模型
    wav2vec_dir = "models/wav2vec2/"
    if os.path.exists(wav2vec_dir):
        files = [f for f in os.listdir(wav2vec_dir) 
                if f.endswith(('.safetensors', '.bin'))]
        if files:
            print(f"   ✅ Wav2Vec 模型: {len(files)} 个文件")
            for f in files:
                print(f"      - {f}")
        else:
            print(f"   ⚠️  Wav2Vec 模型目录存在但为空")
    else:
        print(f"   ⚠️  Wav2Vec 模型目录不存在: {wav2vec_dir}")
    
    # 检查静音嵌入
    silence_path = "genesis/custom_nodes/Comfyui/ComfyUI-WanVideoWrapper/multitalk/encoded_silence.safetensors"
    if os.path.exists(silence_path):
        print(f"   ✅ encoded_silence.safetensors")
    else:
        print(f"   ⚠️  encoded_silence.safetensors 不存在")
        print(f"      位置: {silence_path}")
    
    print("\n=== 检查完成 ===")

if __name__ == "__main__":
    check_dependencies()
```

---

## 快速修复指南

### 错误 1: No module named 'color_matcher'
```bash
pip install color-matcher
```

### 错误 2: No module named 'torchaudio'
```bash
pip install torchaudio
```

### 错误 3: Wav2Vec 模型未找到
1. 下载 Wav2Vec 模型
2. 放置到 `models/wav2vec2/` 目录
3. 或使用无音频模式

### 错误 4: encoded_silence.safetensors 未找到
- 通常随 ComfyUI-WanVideoWrapper 一起提供
- 如果缺失，无音频模式会使用替代方案

---

## 已安装的依赖

- ✅ **color-matcher** (v0.6.0) - 2025-11-14 安装
  - 包含: matplotlib, imageio, docutils 等子依赖

---

## 注意事项

1. **color-matcher 性能**: 颜色匹配会增加处理时间，如果不需要可以禁用
2. **Wav2Vec 模型大小**: 模型文件通常较大（数百MB），确保有足够磁盘空间
3. **内存使用**: 带音频模式会使用更多内存，建议启用 `force_offload` 和 `tiled_vae`
