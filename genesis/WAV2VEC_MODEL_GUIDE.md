# Wav2Vec模型下载指南

## 问题
```
[WARNING] No Wav2Vec model found in models/wav2vec2/, audio will be skipped
```

## 说明

Wav2Vec模型用于InfiniteTalk的音频驱动口型同步功能。如果没有这个模型：
- ✅ InfiniteTalk仍然可以工作（生成视频）
- ❌ 但不会有音频驱动的口型同步效果

## 模型位置

模型应该放在：
```
models/wav2vec2/
```

## 推荐模型

### 中文音频（推荐）
**模型**: TencentGameMate/chinese-wav2vec2-base
**文件名**: 可以命名为 `chinese-wav2vec2-base.safetensors` 或 `.bin`

### 英文音频
**模型**: facebook/wav2vec2-base-960h
**文件名**: 可以命名为 `wav2vec2-base-960h.safetensors` 或 `.bin`

## 下载方法

### 方法1: 从Hugging Face下载

1. 访问模型页面：
   - 中文: https://huggingface.co/TencentGameMate/chinese-wav2vec2-base
   - 英文: https://huggingface.co/facebook/wav2vec2-base-960h

2. 下载模型文件（.safetensors 或 .bin格式）

3. 放到 `models/wav2vec2/` 目录

### 方法2: 使用git-lfs

```bash
# 安装git-lfs
git lfs install

# 克隆模型（中文）
cd models/wav2vec2/
git clone https://huggingface.co/TencentGameMate/chinese-wav2vec2-base

# 或克隆模型（英文）
git clone https://huggingface.co/facebook/wav2vec2-base-960h
```

### 方法3: 从ComfyUI复制

如果你已经在ComfyUI中使用过这些模型：

```
从: E:\liliyuanshangmie\Fuxkcomfy_lris_kernel_gen2-4_speed_safe\FuxkComfy\models\wav2vec2\
到: E:\liliyuanshangmie\genesis_hand\genesis\models\wav2vec2\
```

## 文件结构示例

```
models/
└── wav2vec2/
    ├── chinese-wav2vec2-base.safetensors  (或 .bin)
    └── config.json (可选)
```

## 验证安装

运行InfiniteTalk，应该看到：
```
[DEBUG] Loading Wav2Vec model...
[DEBUG] Using Wav2Vec model: chinese-wav2vec2-base.safetensors
[DEBUG] Wav2Vec model loaded
```

而不是：
```
[WARNING] No Wav2Vec model found in models/wav2vec2/
```

## 不使用音频的情况

如果你不需要音频驱动的口型同步：
1. **不要上传音频文件**
2. InfiniteTalk会正常工作，只是没有口型同步
3. 不需要下载Wav2Vec模型

## 当前错误分析

根据你的日志：
```
[WARNING] No Wav2Vec model found in models/wav2vec2/, audio will be skipped
[WARNING] Audio processing failed: Wav2Vec model not found
[INFO] Continuing without audio...
```

这部分是正常的，程序会继续运行。

但后面的错误：
```
2025-11-14 00:48:03,058 - ERROR - Error during sampling: 'NoneType' object is not subscriptable
```

这是另一个问题，与Wav2Vec无关。这个错误发生在采样器内部。

## 下一步

### 选项A: 不使用音频（推荐先测试）
1. **不要上传音频文件**
2. 重新运行InfiniteTalk
3. 查看是否能成功生成视频

### 选项B: 下载Wav2Vec模型
1. 从上面的方法中选择一个下载模型
2. 放到 `models/wav2vec2/` 目录
3. 重新运行InfiniteTalk并上传音频

## 关于当前的NoneType错误

这个错误不是因为缺少Wav2Vec模型。根据日志：
```
[DEBUG] Image embeds shape: N/A
```

这说明`image_embeds`的格式有问题。我已经添加了更多调试信息，下次运行时应该能看到：
```
[DEBUG] MultiTalk node result type: ...
[DEBUG] MultiTalk node result length: ...
[DEBUG] Image embeds type: ...
[DEBUG] Image embeds keys: [...]
[DEBUG] multitalk_sampling: True
[DEBUG] multitalk_start_image: ...
[DEBUG] VAE in image_embeds: ...
```

这些信息会帮助定位真正的问题。

## 测试建议

**先不上传音频文件测试**：
```
Mode: InfiniteTalk
Image: 上传图片
Prompt: 一个女孩在说话
Steps: 20
CFG: 6.0
Shift: 5.0
Scheduler: unipc 或 dpm++_sde
Frame Window: 117
Motion Frame: 25
Audio: 不上传  <-- 重要！
```

如果这样能成功，再考虑添加音频支持。
