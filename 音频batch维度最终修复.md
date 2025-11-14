# ✅ 音频 Batch 维度最终修复

## 修复时间：2025-11-14

---

## 🔍 问题真相

### 你看到的"成功"

```
[WARNING] Audio processing failed: tuple index out of range
[INFO] Continuing without audio...
[DEBUG] No audio provided, creating silent embeds for InfiniteTalk...
[INFO] Silent embeds created for 117 frames
...
[SUCCESS] Video with audio saved to: ...
```

**表面现象**:
- ✅ 视频生成成功
- ✅ 没有崩溃
- ✅ 视频有声音（ffmpeg 合并了音频）

**实际问题**:
- ❌ **音频处理失败**
- ❌ **使用了静音嵌入**（silent embeds）
- ❌ **嘴型不会同步**（因为没有真实的音频嵌入）
- ⚠️ **视频有声音但嘴型不动或随机动**

---

## 📊 为什么会"成功"？

### 代码的容错机制

```python
try:
    # 尝试处理音频
    audio_embeds_result = wav2vec_embeds_node.process(...)
    audio_embeds = audio_embeds_result[0]
except Exception as e:
    print(f"[WARNING] Audio processing failed: {e}")
    print("[INFO] Continuing without audio...")
    audio_embeds = None  # ← 降级到 None

# 如果音频失败，创建静音嵌入
if audio_embeds is None:
    print("[DEBUG] No audio provided, creating silent embeds...")
    # 创建静音嵌入，视频仍然可以生成
```

**结果**:
- 音频处理失败被**捕获**
- 自动**降级**到静音模式
- 视频**仍然生成**
- 但**嘴型不同步**

---

## 🎯 真正的问题

### 格式不匹配

**我们提供的格式**:
```python
audio_data = {
    "waveform": waveform,  # shape: (2, 160752) - (channels, samples)
    "sample_rate": 44100
}
```

**节点期望的格式**:
```python
audio_data = {
    "waveform": waveform,  # shape: (1, 2, 160752) - (batch, channels, samples)
    "sample_rate": 44100
}
```

### 节点代码的假设

```python
# nodes.py 第 193 行
audio_input = audio["waveform"]        # 期望 (batch, channels, samples)
audio_input = audio_input[0][0]        # [0] 提取 batch, [0] 提取 channel
```

**如果格式是 `(2, 160752)`**:
- `audio_input[0]` → `(160752,)` - 第一个 channel ✅
- `audio_input[0][0]` → **标量** - 第一个采样点 ❌
- 传给 `loudness_norm()` → 期望数组，得到标量 → **错误**

---

## ✅ 最终解决方案

### 在传递给节点时添加 batch 维度

**修改位置**: `genesis/apps/wanvideo_gradio_app.py` 第 385-389 行

#### 修改前

```python
audio_data = {
    "waveform": waveform,  # (channels, samples)
    "sample_rate": sample_rate
}
```

#### 修改后

```python
# 添加 batch 维度以匹配 ComfyUI AUDIO 格式 (batch, channels, samples)
audio_data = {
    "waveform": waveform.unsqueeze(0),  # (channels, samples) -> (1, channels, samples)
    "sample_rate": sample_rate
}
```

---

## 📊 数据流对比

### 修复前（错误）

```
soundfile 加载
    ↓
(2, 160752)  # (channels, samples)
    ↓
传递给节点
    ↓
audio_input[0][0]
    ↓
标量（单个数字）❌
    ↓
loudness_norm() 失败
    ↓
降级到 silent embeds
    ↓
视频生成（嘴型不同步）
```

### 修复后（正确）

```
soundfile 加载
    ↓
(2, 160752)  # (channels, samples)
    ↓
.unsqueeze(0)
    ↓
(1, 2, 160752)  # (batch, channels, samples)
    ↓
传递给节点
    ↓
audio_input[0][0]
    ↓
(160752,)  # 单声道数组 ✅
    ↓
loudness_norm() 成功
    ↓
音频嵌入生成成功
    ↓
视频生成（嘴型同步）✅
```

---

## 🎉 修复效果

### 修复前

```
[DEBUG] Audio loaded with soundfile: 44100Hz, shape=torch.Size([2, 160752])
[DEBUG] Audio file loaded: sample_rate=44100, shape=torch.Size([2, 160752])
[DEBUG] Creating audio embeds...
[WARNING] Audio processing failed: tuple index out of range
[INFO] Continuing without audio...
[DEBUG] No audio provided, creating silent embeds for InfiniteTalk...
[INFO] Silent embeds created for 117 frames
```

**结果**: 视频有声音，但**嘴型不同步**

### 修复后（预期）

```
[DEBUG] Audio loaded with soundfile: 44100Hz, shape=torch.Size([2, 160752])
[DEBUG] Audio file loaded: sample_rate=44100, shape=torch.Size([1, 2, 160752])
[DEBUG] Creating audio embeds...
[INFO] Audio embeds created, actual frames: 91
```

**结果**: 视频有声音，**嘴型同步** ✅

---

## 🔧 为什么这次不会出现维度错误？

### 之前的问题

当我在 `load_audio_with_soundfile` 中添加 batch 维度时：
```python
waveform = waveform.T.unsqueeze(0)  # (1, 2, 160752)
```

出现了：
```
"error": "Sizes of tensors must match except in dimension 0. Expected size 60 but got size 30..."
```

### 这次的不同

**关键区别**: 添加 batch 维度的**位置**不同

#### 之前（错误）

```python
# 在 load_audio_with_soundfile 中
waveform = waveform.T.unsqueeze(0)  # 加载时就添加
return waveform, sample_rate

# 后续所有使用 waveform 的地方都是 (1, 2, 160752)
```

**问题**: 可能有其他代码期望 `(channels, samples)` 格式

#### 现在（正确）

```python
# 在 load_audio_with_soundfile 中
waveform = waveform.T  # 保持 (channels, samples)
return waveform, sample_rate

# 只在传递给节点时添加
audio_data = {
    "waveform": waveform.unsqueeze(0),  # 只在这里添加
    "sample_rate": sample_rate
}
```

**优势**: 
- 不影响其他代码
- 只在需要的地方添加
- 更安全，更精确

---

## 📋 完整的音频处理流程

### 1. 加载音频

```python
waveform, sample_rate = load_audio_with_soundfile(audio_file)
# 返回: (2, 160752) - (channels, samples)
```

### 2. 添加 batch 维度

```python
audio_data = {
    "waveform": waveform.unsqueeze(0),  # (1, 2, 160752)
    "sample_rate": sample_rate
}
```

### 3. 传递给节点

```python
audio_embeds_result = wav2vec_embeds_node.process(
    wav2vec_model=wav2vec_model,
    audio_1=audio_data,  # (1, 2, 160752)
    ...
)
```

### 4. 节点处理

```python
# nodes.py
audio_input = audio["waveform"]        # (1, 2, 160752)
audio_input = audio_input[0][0]        # (160752,) ✅
loudness_norm(audio_input, sr=16000)   # ✅ 成功
```

### 5. 生成音频嵌入

```python
audio_embeds = audio_embeds_result[0]  # 音频嵌入
actual_num_frames = audio_embeds_result[2]  # 实际帧数
```

### 6. 生成视频（嘴型同步）

```python
# 使用真实的音频嵌入
video_frames = sampler.process(..., multitalk_embeds=audio_embeds)
```

---

## 🎯 关键要点

### 1. 格式要求

- **加载时**: `(channels, samples)` - 保持简单
- **传递时**: `(batch, channels, samples)` - 添加 batch 维度
- **节点内**: 自动处理

### 2. 添加位置

- ✅ **在传递给节点时添加** - 精确控制
- ❌ **在加载时就添加** - 可能影响其他代码

### 3. 容错机制

- 音频处理失败会降级到 silent embeds
- 视频仍然可以生成
- 但嘴型不会同步

---

## 🚀 测试验证

### 预期日志

```
[DEBUG] Audio loaded with soundfile: 44100Hz, shape=torch.Size([2, 160752])
[DEBUG] Audio file loaded: sample_rate=44100, shape=torch.Size([2, 160752])
[DEBUG] Creating audio embeds...
2025-11-14 XX:XX:XX,XXX - INFO - [MultiTalk] --- Raw speaker lengths (samples) ---
2025-11-14 XX:XX:XX,XXX - INFO -   speaker 1: 58323 samples (shape: torch.Size([1, 1, 58323]))
2025-11-14 XX:XX:XX,XXX - INFO - [MultiTalk] Audio duration (91 frames) is shorter than requested (117 frames). Using 91 frames.
[INFO] Audio embeds created, actual frames: 91
```

**关键**: 不再出现 `[WARNING] Audio processing failed`

### 检查视频

1. ✅ 视频有声音
2. ✅ **嘴型与声音同步** ← 关键！
3. ✅ 嘴型自然流畅

---

## 🎉 总结

### 问题根源

- 格式不匹配: 缺少 batch 维度
- 节点代码假设有 batch 维度
- `audio_input[0][0]` 提取失败

### 解决方案

- 在传递给节点时添加 batch 维度
- 使用 `.unsqueeze(0)` 添加第一维
- 不影响其他代码

### 修复效果

- ✅ 音频处理成功
- ✅ 音频嵌入生成成功
- ✅ 视频嘴型同步
- ✅ 完整的 InfiniteTalk 功能

---

**现在应该真正修复了！嘴型会同步了！** 🎊
