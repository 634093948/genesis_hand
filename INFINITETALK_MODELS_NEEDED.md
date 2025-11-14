# InfiniteTalk 所需模型清单

根据 ComfyUI InfiniteTalk 工作流分析，以下是所有需要的模型文件。

---

## 📋 模型清单

### 1. WanVideo 主模型 ⚠️ **必需**

#### 位置
```
models/wanvideo/
```

#### 文件
- **wan2.1-i2v-14b-480p-Q8_0.gguf** (约 8-10 GB)
  - 主要的图生视频模型
  - GGUF 量化版本（Q8_0）
  - 用于 InfiniteTalk 的基础模型

#### 下载链接
```
https://huggingface.co/city96/Wan2.1-I2V-14B-480P-gguf/tree/main
或
https://huggingface.co/Kijai/WanVideo_comfy_GGUF/tree/main
```

#### 替代版本
- **fp16 版本**: `wan2.1-i2v-14b-480p-fp16.safetensors` (约 28 GB)
- **fp8 版本**: `wan2.1-i2v-14b-480p-fp8.safetensors` (约 14 GB)

---

### 2. VAE 模型 ⚠️ **必需**

#### 位置
```
models/wanvideo/
```

#### 文件
- **Wan2_1_VAE_bf16.safetensors** (约 300 MB)
  - 视频编码/解码器
  - BF16 精度版本

#### 下载链接
```
https://huggingface.co/Kijai/WanVideo_comfy/tree/main
```

---

### 3. Wav2Vec 模型 ⚠️ **带音频模式必需**

#### 位置
```
models/wav2vec2/
```

#### 文件（任选其一）
- **wav2vec2-chinese-base_fp16.safetensors** (约 300 MB)
  - 中文音频特征提取
  - FP16 精度
  
- **chinese-wav2vec2-base.safetensors** (约 300 MB)
  - 腾讯中文 Wav2Vec 模型

#### 下载链接
```
手动下载:
https://huggingface.co/TencentGameMate/chinese-wav2vec2-base

或使用 DownloadAndLoadWav2VecModel 节点自动下载
```

#### 注意
- **无音频模式不需要此模型**
- 使用静音嵌入可以跳过此模型

---

### 4. CLIP Vision 模型 ⚠️ **可选（推荐）**

#### 位置
```
models/clip_vision/
```

#### 文件
- **clip_vision_h.safetensors** (约 3.7 GB)
  - CLIP Vision 大模型
  - 用于图像理解和条件控制

#### 下载链接
```
https://huggingface.co/h94/IP-Adapter/tree/main/models/image_encoder
或
https://huggingface.co/openai/clip-vit-large-patch14
```

#### 注意
- ComfyUI 工作流注释说明："Clip vision is not strictly necessary"
- 但使用它可以提升生成质量

---

### 5. MultiTalk 模型 ⚠️ **InfiniteTalk 模式必需**

#### 位置
```
models/wanvideo/InfiniteTalk/
```

#### 文件
- **multitalk_model.safetensors** 或相关文件
  - InfiniteTalk 特定的模型组件
  - 用于长视频生成和唇形同步

#### 下载链接
```
GGUF 版本:
https://huggingface.co/Kijai/WanVideo_comfy_GGUF/tree/main/InfiniteTalk

FP8 版本:
https://huggingface.co/Kijai/WanVideo_comfy_fp8_scaled/tree/main/InfiniteTalk

FP16 版本:
https://huggingface.co/Kijai/WanVideo_comfy/tree/main/InfiniteTalk
```

#### 注意
- **必须与主模型的精度/格式匹配**
- 如果主模型是 GGUF，MultiTalk 也必须是 GGUF
- 不能混用 GGUF 和非 GGUF 版本

---

### 6. T5 文本编码器 ⚠️ **必需**

#### 位置
```
models/text_encoders/t5/
或
genesis/custom_nodes/Comfyui/ComfyUI-WanVideoWrapper/configs/T5_tokenizer/
```

#### 文件
- T5 tokenizer 配置文件（已包含在项目中）
- T5 模型权重（如果需要）

#### 注意
- 配置文件已经包含在 `ComfyUI-WanVideoWrapper/configs/T5_tokenizer/` 中
- 可能不需要额外下载

---

## 📊 模型优先级

### 立即需要（无音频模式）
1. ✅ **encoded_silence.safetensors** - 已存在
2. ⚠️ **WanVideo 主模型** (GGUF Q8_0) - 需要下载
3. ⚠️ **VAE 模型** (BF16) - 需要下载
4. ⚠️ **MultiTalk 模型** (GGUF) - 需要下载

### 推荐添加
5. ⚠️ **CLIP Vision** - 提升质量

### 带音频模式额外需要
6. ⚠️ **Wav2Vec 模型** - 音频处理

---

## 💾 存储空间需求

### 最小配置（GGUF Q8_0）
- WanVideo 主模型: ~10 GB
- VAE: ~0.3 GB
- MultiTalk: ~2 GB
- **总计: ~12.3 GB**

### 推荐配置（+ CLIP Vision）
- 最小配置: ~12.3 GB
- CLIP Vision: ~3.7 GB
- **总计: ~16 GB**

### 完整配置（+ Wav2Vec）
- 推荐配置: ~16 GB
- Wav2Vec: ~0.3 GB
- **总计: ~16.3 GB**

### 高质量配置（FP16）
- WanVideo 主模型 FP16: ~28 GB
- VAE: ~0.3 GB
- MultiTalk FP16: ~5 GB
- CLIP Vision: ~3.7 GB
- Wav2Vec: ~0.3 GB
- **总计: ~37.3 GB**

---

## 📥 下载指南

### 方法 1：使用 Hugging Face CLI（推荐）

```bash
# 安装 huggingface-hub
pip install huggingface-hub

# 下载 WanVideo 主模型（GGUF Q8_0）
huggingface-cli download city96/Wan2.1-I2V-14B-480P-gguf \
  wan2.1-i2v-14b-480p-Q8_0.gguf \
  --local-dir models/wanvideo

# 下载 VAE
huggingface-cli download Kijai/WanVideo_comfy \
  Wan2_1_VAE_bf16.safetensors \
  --local-dir models/wanvideo

# 下载 MultiTalk（GGUF）
huggingface-cli download Kijai/WanVideo_comfy_GGUF \
  InfiniteTalk/multitalk_model.safetensors \
  --local-dir models/wanvideo

# 下载 CLIP Vision
huggingface-cli download h94/IP-Adapter \
  models/image_encoder/model.safetensors \
  --local-dir models/clip_vision \
  --local-dir-use-symlinks False

# 下载 Wav2Vec（可选）
huggingface-cli download TencentGameMate/chinese-wav2vec2-base \
  --local-dir models/wav2vec2
```

### 方法 2：手动下载

1. 访问 Hugging Face 模型页面
2. 点击 "Files and versions" 标签
3. 下载所需文件
4. 放置到对应目录

### 方法 3：从 ComfyUI 复制（如果已有）

如果你的 ComfyUI 已经下载了这些模型，可以直接复制或创建符号链接：

```bash
# 运行检查脚本
python check_and_link_models.py
```

---

## 🔍 模型检查脚本

使用以下脚本检查缺失的模型：

```bash
python check_infinitetalk_deps.py
```

---

## ⚙️ 模型配置

### 在 Gradio UI 中
模型会自动从以下目录加载：
- `models/wanvideo/`
- `models/wav2vec2/`
- `models/clip_vision/`

### 精度选择建议

| GPU VRAM | 推荐配置 | 主模型 | 速度 | 质量 |
|----------|---------|--------|------|------|
| 8-12 GB | 最小 | GGUF Q8_0 | 慢 | 中 |
| 12-16 GB | 推荐 | GGUF Q8_0 + CLIP | 中 | 高 |
| 16-24 GB | 高质量 | FP8 | 快 | 高 |
| 24+ GB | 最佳 | FP16 | 最快 | 最高 |

---

## 🚨 重要注意事项

### 1. 模型版本匹配 ⚠️
**主模型和 MultiTalk 必须匹配！**

```
✅ 正确组合:
- wan2.1-i2v-14b-480p-Q8_0.gguf + InfiniteTalk GGUF
- wan2.1-i2v-14b-480p-fp16.safetensors + InfiniteTalk FP16

❌ 错误组合:
- wan2.1-i2v-14b-480p-Q8_0.gguf + InfiniteTalk FP16
- 会导致加载失败或生成错误
```

### 2. 文件命名
确保文件名与配置匹配，或在代码中指定正确的文件名。

### 3. 模型路径
所有模型应放在 `models/` 目录下的对应子目录中。

---

## 📝 当前状态

### 已有文件 ✅
- `encoded_silence.safetensors` (1.6 MB)
- `wav2vec2_config.json`

### 需要下载 ⚠️
1. **WanVideo 主模型** (~10 GB)
2. **VAE 模型** (~300 MB)
3. **MultiTalk 模型** (~2 GB)
4. **CLIP Vision** (~3.7 GB) - 可选
5. **Wav2Vec 模型** (~300 MB) - 带音频模式需要

### 总下载量
- **最小**: ~12.3 GB（无音频模式）
- **推荐**: ~16 GB（包含 CLIP Vision）
- **完整**: ~16.3 GB（包含所有功能）

---

## 🎯 快速开始

### 步骤 1：下载核心模型
```bash
# 创建目录
mkdir -p models/wanvideo models/wav2vec2 models/clip_vision

# 下载最小配置（~12 GB）
# 1. WanVideo 主模型 (GGUF Q8_0)
# 2. VAE
# 3. MultiTalk
```

### 步骤 2：验证模型
```bash
python check_infinitetalk_deps.py
```

### 步骤 3：测试
```bash
# 启动 Gradio UI
python genesis/apps/wanvideo_gradio_app.py

# 测试无音频模式
```

---

## 📚 相关文档

- `INFINITETALK_DEPS_COMPLETE.md` - 依赖完整报告
- `INFINITETALK_READY.md` - 准备就绪检查
- `models/wav2vec2/README.md` - Wav2Vec 模型指南
- `check_and_link_models.py` - 模型检查脚本

---

**下一步**: 根据你的 GPU 内存和需求，选择合适的模型配置并开始下载。
