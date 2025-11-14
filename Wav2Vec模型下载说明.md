# Wav2Vec 模型下载说明

## 当前状态

你的 ComfyUI 中**没有 Wav2Vec 模型**，只有 Whisper 模型。

InfiniteTalk 的音频功能需要 Wav2Vec 模型才能工作。

---

## 解决方案

### 方案 1：使用无音频模式（推荐，立即可用）✅

**无需下载任何模型**，InfiniteTalk 会自动使用静音嵌入。

**优点**：
- ✅ 立即可用
- ✅ 不占用额外空间
- ✅ 生成速度更快

**使用方法**：
1. 启动 UI
2. 上传图片
3. **不要上传音频文件**
4. 选择 InfiniteTalk 模式
5. 生成视频

---

### 方案 2：下载 Wav2Vec 模型（带音频功能）

如果需要音频驱动的唇形同步，下载以下模型之一：

#### 选项 A：中文 Wav2Vec（推荐）

**模型名称**: `TencentGameMate/chinese-wav2vec2-base`

**大小**: ~300 MB

**下载方法 1 - 使用 Hugging Face CLI**:
```bash
pip install huggingface-hub

huggingface-cli download TencentGameMate/chinese-wav2vec2-base \
  --local-dir models/wav2vec2 \
  --local-dir-use-symlinks False
```

**下载方法 2 - 手动下载**:
1. 访问: https://huggingface.co/TencentGameMate/chinese-wav2vec2-base
2. 下载以下文件到 `models/wav2vec2/`:
   - `pytorch_model.bin` 或 `model.safetensors`
   - `config.json`
   - `preprocessor_config.json`

#### 选项 B：英文 Wav2Vec

**模型名称**: `facebook/wav2vec2-base-960h`

**大小**: ~360 MB

**下载**:
```bash
huggingface-cli download facebook/wav2vec2-base-960h \
  --local-dir models/wav2vec2 \
  --local-dir-use-symlinks False
```

---

## 验证安装

下载完成后，运行：

```bash
python313\python.exe check_infinitetalk_deps.py
```

应该看到：
```
✅ Wav2Vec 模型 - 存在
```

---

## 目录结构

下载后的目录应该是：

```
models/
└── wav2vec2/
    ├── pytorch_model.bin  或  model.safetensors
    ├── config.json
    └── preprocessor_config.json
```

---

## 常见问题

### Q: 必须下载 Wav2Vec 模型吗？
**A**: 不必须。无音频模式完全可用，会自动使用静音嵌入。

### Q: 下载哪个模型更好？
**A**: 
- 如果音频是中文 → `TencentGameMate/chinese-wav2vec2-base`
- 如果音频是英文 → `facebook/wav2vec2-base-960h`

### Q: 可以使用 Whisper 模型吗？
**A**: 不可以。InfiniteTalk 专门需要 Wav2Vec 模型，Whisper 是不同的架构。

### Q: 下载速度很慢怎么办？
**A**: 
1. 使用国内镜像（如果有）
2. 使用下载工具
3. 或者直接使用无音频模式

---

## 当前配置

- ✅ **InfiniteTalk 模型**: 已链接（3 个版本）
- ✅ **VAE 模型**: 已链接
- ✅ **CLIP Vision**: 已链接
- ✅ **静音嵌入**: 已存在
- ⚠️ **Wav2Vec 模型**: 未下载（可选）

---

**建议**: 先使用无音频模式测试 InfiniteTalk 功能，确认一切正常后再考虑下载 Wav2Vec 模型。
