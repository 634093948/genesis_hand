# InfiniteTalk 采样器错误修复

## 错误信息
```
2025-11-14 01:17:35,291 - INFO - Multitalk mode: infinitetalk
2025-11-14 01:17:35,292 - ERROR - Error during sampling: 'NoneType' object is not subscriptable
```

## 问题根源

在 `wanvideo_gradio_app.py` 的 `generate_image_to_video()` 函数中，InfiniteTalk 模式的采样器调用返回了 `None`，导致在尝试访问 `result[0]` 时出现 `'NoneType' object is not subscriptable` 错误。

### 具体位置
- **文件**: `genesis/apps/wanvideo_gradio_app.py`
- **函数**: `generate_image_to_video()`
- **错误行**: 第571行 `samples = result[0]`

## 问题分析

对比 T2V（文本生视频）的成功实现，发现 I2V（图生视频）的采样器参数存在以下问题：

1. **参数顺序不匹配**: I2V 使用了不同的参数顺序和结构
2. **多余参数**: 包含了 T2V 中没有使用的参数（如 `batched_cfg`, `rope_function`, `start_step`, `end_step`, `add_noise_to_samples`）
3. **参数验证不足**: 缺少对 `text_embeds` 的详细验证

## 修复方案

参考 T2V 的成功实现（第920-933行），调整 I2V 的采样器参数：

### 修改前（第507-564行）
```python
sampler_args = {
    "model": model,
    "image_embeds": image_embeds,
    "shift": shift,
    "steps": steps,
    "cfg": cfg,
    "seed": seed,
    "scheduler": actual_scheduler,
    "riflex_freq_index": 0,
    "text_embeds": text_embeds,
    "force_offload": True,
    "batched_cfg": False,
    "rope_function": "default",
    "start_step": 0,
    "end_step": -1,
    "add_noise_to_samples": False
}
```

### 修改后
```python
sampler_args = {
    "model": model,
    "image_embeds": image_embeds,
    "steps": steps,
    "cfg": cfg,
    "shift": shift,
    "seed": seed,
    "scheduler": actual_scheduler,
    "riflex_freq_index": 0,
    "force_offload": True,
    "text_embeds": text_embeds
}
```

### 关键改进

1. **调整参数顺序**: 匹配 `WanVideoSampler.process()` 的预期签名
2. **移除多余参数**: 删除 `batched_cfg`, `rope_function`, `start_step`, `end_step`, `add_noise_to_samples`
3. **增强验证**: 添加 `text_embeds` 的详细验证日志
4. **保持一致性**: 与 T2V 的参数传递方式保持一致

## 验证要点

修复后，采样器调用应该：
1. 正确返回结果元组而不是 `None`
2. `result[0]` 包含有效的样本张量
3. 日志显示正确的参数类型和值

## 相关文件

- `genesis/apps/wanvideo_gradio_app.py` - 主要修复文件
- T2V 参考实现：第920-933行
- I2V 修复位置：第507-571行

## 音频功能修复

### 问题 1: 加载音频节点不存在
原代码使用了不存在的 `LoadAudio` 节点来加载音频文件。

### 修复方案
直接使用 `torchaudio` 加载音频文件，并转换为 `MultiTalkWav2VecEmbeds` 节点所需的格式：

```python
# 修改前（错误）
audio_loader = NODE_CLASS_MAPPINGS['LoadAudio']()  # 节点不存在
audio_data = audio_loader.load_audio(audio=audio_file)[0]

# 修改后（正确）
import torchaudio
waveform, sample_rate = torchaudio.load(audio_file)
audio_data = {
    "waveform": waveform,
    "sample_rate": sample_rate
}
```

### 音频处理流程

1. **加载 Wav2Vec 模型**: 使用 `Wav2VecModelLoader` 节点
2. **加载音频文件**: 使用 `torchaudio.load()` 直接加载
3. **创建音频嵌入**: 使用 `MultiTalkWav2VecEmbeds` 节点处理
4. **传递给采样器**: 通过 `multitalk_embeds` 参数

### 音频格式要求

音频数据必须是包含以下键的字典：
- `waveform`: PyTorch 张量，形状为 `(channels, samples)`
- `sample_rate`: 整数，采样率（通常为 16000 或 44100）

### 问题 2: 无音频时传递 None 导致崩溃 ⚠️

**严重问题**: 采样器的 multitalk_sampling 代码路径**不支持** `multitalk_embeds=None`

在 `nodes_sampler.py` 第2017行和2039-2064行，代码直接访问 `multitalk_embeds` 而不检查是否为 `None`：

```python
# 第2017行 - 如果multitalk_embeds是None会崩溃
if len(multitalk_embeds['audio_features'])==2 and ...

# 第2039-2064行 - 如果multitalk_audio_embeds是None会崩溃
audio_embedding = multitalk_audio_embeds  
human_num = len(audio_embedding)  # TypeError!
total_frames = len(audio_embedding[0])  # TypeError!
```

### 修复方案 2: 使用 MultiTalkSilentEmbeds

当没有音频时，必须使用 `MultiTalkSilentEmbeds` 节点创建静音嵌入，而不是传递 `None`：

```python
# 修改前（错误）
if audio_file is None:
    audio_embeds = None
    sampler_args["multitalk_embeds"] = None  # 会导致采样器崩溃！

# 修改后（正确）
if audio_embeds is None:
    silent_embeds_node = NODE_CLASS_MAPPINGS['MultiTalkSilentEmbeds']()
    silent_result = silent_embeds_node.process(num_frames=frame_window_size)
    audio_embeds = silent_result[0]  # 有效的静音嵌入
    
sampler_args["multitalk_embeds"] = audio_embeds  # 始终传递有效对象
```

### MultiTalkSilentEmbeds 工作原理

该节点加载预编码的静音音频嵌入（`encoded_silence.safetensors`），并重复到所需的帧数：

```python
{
    "audio_features": repeated_silence_tensor,  # 形状: (num_frames, ...)
    "audio_scale": 1.0,
    "audio_cfg_scale": 1.0,
    "ref_target_masks": None
}
```

## 测试建议

1. ✅ 使用 InfiniteTalk 模式生成视频（无音频）
2. ✅ 使用 InfiniteTalk 模式生成视频（带音频）
   - 确保 Wav2Vec 模型已下载到 `models/wav2vec2/` 目录
   - 支持的音频格式：WAV, MP3, FLAC 等
3. 检查日志确认采样器正常返回结果
4. 验证生成的视频质量和音频同步
