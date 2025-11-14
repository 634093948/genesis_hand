# InfiniteTalk 音频视频合成修复

## ✅ 已完成的修复

### 1. Wav2Vec 参数问题 ✅
- 添加了 `base_precision` 和 `load_device` 参数
- 在 UI 中添加了可选择的参数控件
- 参数已正确传递到音频加载函数

### 2. UI 参数控件 ✅
```python
# Wav2Vec 模型参数
with gr.Accordion("🎙️ Wav2Vec 音频模型设置", open=False):
    wav2vec_precision = gr.Radio(
        choices=["fp16", "fp32", "bf16"],
        value="fp16",
        label="模型精度 (Precision)"
    )
    wav2vec_device = gr.Radio(
        choices=["main_device", "offload_device", "cpu"],
        value="main_device",
        label="加载设备 (Device)"
    )
```

---

## ⚠️ 视频没有声音的原因

### 问题定位

**当前视频保存代码**（第 683 行）:
```python
imageio.mimwrite(str(video_path), video_array, fps=fps, quality=8, codec='libx264')
```

**问题**:
- `imageio.mimwrite` 只保存视频帧
- **没有包含音频轨道**
- 音频文件被处理了，但没有合并到最终视频中

### 原因分析

1. **音频嵌入 ≠ 音频轨道**
   - `audio_embeds` 用于控制视频生成（嘴型同步）
   - 但不会自动添加到输出视频的音频轨道

2. **imageio 的限制**
   - `imageio.mimwrite` 主要用于保存图像序列
   - 不支持直接添加音频轨道

3. **需要后处理**
   - 生成视频后，需要使用 ffmpeg 将音频合并进去

---

## 🔧 解决方案

### 方案 1: 使用 ffmpeg 合并音频（推荐）

在视频保存后，添加音频合并步骤：

```python
# 保存无声视频
video_path_no_audio = output_dir / f"{mode.lower()}_{timestamp}_no_audio.mp4"
imageio.mimwrite(str(video_path_no_audio), video_array, fps=fps, quality=8, codec='libx264')

# 如果有音频文件，合并音频
if audio_file is not None and audio_file != "":
    import subprocess
    video_path_with_audio = output_dir / f"{mode.lower()}_{timestamp}.mp4"
    
    # 使用 ffmpeg 合并
    cmd = [
        'ffmpeg', '-y',
        '-i', str(video_path_no_audio),  # 输入视频
        '-i', audio_file,                 # 输入音频
        '-c:v', 'copy',                   # 复制视频流（不重新编码）
        '-c:a', 'aac',                    # 音频编码为 AAC
        '-shortest',                      # 使用较短的流长度
        str(video_path_with_audio)
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"[SUCCESS] Video with audio saved to: {video_path_with_audio}")
        video_path = video_path_with_audio
        
        # 删除临时无声视频
        video_path_no_audio.unlink()
    except Exception as e:
        print(f"[WARNING] Failed to merge audio: {e}")
        print(f"[INFO] Using video without audio: {video_path_no_audio}")
        video_path = video_path_no_audio
else:
    video_path = video_path_no_audio
```

### 方案 2: 使用 moviepy（备选）

```python
from moviepy.editor import VideoFileClip, AudioFileClip

# 保存无声视频
video_path_no_audio = output_dir / f"{mode.lower()}_{timestamp}_no_audio.mp4"
imageio.mimwrite(str(video_path_no_audio), video_array, fps=fps, quality=8, codec='libx264')

# 如果有音频，合并
if audio_file is not None and audio_file != "":
    try:
        video_clip = VideoFileClip(str(video_path_no_audio))
        audio_clip = AudioFileClip(audio_file)
        
        # 裁剪音频到视频长度
        audio_clip = audio_clip.subclip(0, video_clip.duration)
        
        # 合并
        final_clip = video_clip.set_audio(audio_clip)
        video_path_with_audio = output_dir / f"{mode.lower()}_{timestamp}.mp4"
        final_clip.write_videofile(str(video_path_with_audio), codec='libx264', audio_codec='aac')
        
        # 清理
        video_clip.close()
        audio_clip.close()
        final_clip.close()
        video_path_no_audio.unlink()
        
        video_path = video_path_with_audio
    except Exception as e:
        print(f"[WARNING] Failed to merge audio: {e}")
        video_path = video_path_no_audio
else:
    video_path = video_path_no_audio
```

---

## 📝 修改位置

**文件**: `genesis/apps/wanvideo_gradio_app.py`
**函数**: `generate_image_to_video`
**行号**: 约 680-685

**当前代码**:
```python
try:
    import imageio
    imageio.mimwrite(str(video_path), video_array, fps=fps, quality=8, codec='libx264')
    print(f"[SUCCESS] Video saved successfully to: {video_path}")
except Exception as save_error:
    print(f"[ERROR] Failed to save video: {save_error}")
```

**需要修改为**: 添加音频合并逻辑（见上面的方案）

---

## 🎯 推荐实现

使用 **方案 1 (ffmpeg)**，因为:
1. ✅ 速度快（不需要重新编码视频）
2. ✅ 质量好（视频流直接复制）
3. ✅ 依赖少（ffmpeg 通常已安装）
4. ✅ 稳定性高

---

## 📋 完整流程

1. **生成视频帧** ✅ (已完成)
2. **处理音频嵌入** ✅ (已完成，用于嘴型同步)
3. **保存无声视频** ✅ (已完成)
4. **合并音频轨道** ⚠️ (需要添加)
5. **返回带音频的视频** ⚠️ (需要添加)

---

## 🚀 测试步骤

修改后测试:
1. 上传图片
2. 上传音频文件
3. 生成视频
4. 检查输出视频是否有声音

---

## 💡 注意事项

1. **音频长度**
   - 如果音频比视频长，使用 `-shortest` 参数裁剪
   - 如果音频比视频短，可能需要循环或静音填充

2. **音频格式**
   - 输入支持: MP3, WAV, FLAC 等
   - 输出统一为: AAC (兼容性最好)

3. **性能**
   - ffmpeg 复制视频流很快（几秒钟）
   - moviepy 需要重新编码（较慢）

4. **错误处理**
   - 如果音频合并失败，降级到无声视频
   - 保留原始无声视频作为备份

---

## 总结

**当前状态**:
- ✅ 音频加载正常
- ✅ 音频嵌入正常（嘴型同步）
- ✅ 视频生成正常
- ⚠️ 视频没有音频轨道（需要后处理）

**需要添加**: 视频保存后的音频合并步骤

**推荐方案**: 使用 ffmpeg 合并音频（方案 1）
