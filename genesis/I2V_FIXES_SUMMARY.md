# I2V功能全面修复总结

## 修复日期
2025-11-13

## 参考资料
- T2V功能实现
- InfiniteTalk工作流: `Infinite Talk test(1).json`
- 工作流参数: [832, 480, 117, 25, False, 'mkl', False, 'infinitetalk', '']

## 主要修复内容

### 1. 模型加载修复
**问题**: 模型加载参数不正确
**修复**:
- InfiniteTalk模式使用 `load_device="main_device"`
- 其他模式使用 `load_device="offload_device"`
- T5编码器添加 `quantization="disabled"` 参数
- 添加进度回调支持

### 2. 文本编码修复
**问题**: 参数名错误 (`t5_encoder` 应为 `t5`)
**修复**:
```python
text_embeds = text_encoder.process(
    positive_prompt=positive_prompt,
    negative_prompt=negative_prompt,
    t5=t5_encoder,  # 修复: 使用正确的参数名
    force_offload=True,
    use_disk_cache=False,
    device="gpu"
)[0]
```

### 3. InfiniteTalk模式完整实现
**新增功能**:
- CLIP Vision编码支持
- Wav2Vec2音频处理
- MultiTalk音频嵌入
- 正确的参数配置

**关键代码**:
```python
# 加载CLIP Vision
clip_vision_loader = NODE_CLASS_MAPPINGS['LoadCLIPVision']()
clip_vision = clip_vision_loader.load_model(
    model_name="sigclip_vision_patch14_384.safetensors"
)[0]

# 编码图像
clip_vision_encoder = NODE_CLASS_MAPPINGS['WanVideoClipVisionEncode']()
clip_embeds = clip_vision_encoder.process(
    clip_vision=clip_vision,
    image_1=img_tensor,
    strength_1=1.0,
    strength_2=1.0,
    force_offload=True,
    crop="center",
    combine_embeds="average"
)[0]

# 处理音频
wav2vec_loader = NODE_CLASS_MAPPINGS['DownloadAndLoadWav2VecModel']()
wav2vec_model = wav2vec_loader.loadmodel(
    model_name="TencentGameMate/chinese-wav2vec2-base",
    base_precision="fp16",
    load_device="main_device"
)[0]

wav2vec_embeds_node = NODE_CLASS_MAPPINGS['MultiTalkWav2VecEmbeds']()
audio_embeds = wav2vec_embeds_node.process(
    wav2vec_model=wav2vec_model,
    audio_1=audio_data,
    normalize_loudness=True,
    num_frames=frame_window_size,
    fps=fps,
    audio_scale=1.0,
    audio_cfg_scale=1.0,
    multi_audio_type="para"
)[0]
```

### 4. 采样器修复
**问题**: InfiniteTalk需要使用特定的调度器
**修复**:
```python
sampler_args = {
    "model": model,
    "image_embeds": image_embeds,
    "text_embeds": text_embeds,
    "steps": steps,
    "cfg": cfg,
    "shift": shift,
    "seed": seed,
    "force_offload": True,
    "scheduler": "multitalk" if mode == "InfiniteTalk" else scheduler,  # 自动选择调度器
    "riflex_freq_index": 0
}

if mode == "InfiniteTalk" and audio_embeds is not None:
    sampler_args["multitalk_embeds"] = audio_embeds
```

### 5. 解码器修复
**问题**: 
- 使用了错误的方法名 `process` 应为 `decode`
- 缺少必要参数

**修复**:
```python
video_result = decoder.decode(
    vae=vae,
    samples=samples,
    enable_vae_tiling=False,
    tile_x=272,
    tile_y=272,
    tile_stride_x=144,
    tile_stride_y=128,
    normalization="default"
)
```

### 6. WanAnimate模式修复
**问题**: 参数名错误 (`tiled` 应为 `tiled_vae`)
**修复**:
```python
image_embeds = animate_embeds_node.process(
    vae=vae,
    width=width,
    height=height,
    num_frames=num_frames,
    force_offload=True,
    frame_window_size=frame_window_size,
    colormatch=colormatch,
    pose_strength=pose_strength,
    face_strength=face_strength,
    tiled_vae=False,  # 修复: 使用正确的参数名
    ref_images=img_tensor,
    pose_images=pose_imgs,
    face_images=face_imgs
)[0]
```

### 7. Standard I2V模式修复
**问题**: 
- 类名错误 (`WanVideoImageToVideoEmbeds` 应为 `WanVideoImageToVideoEncode`)
- 缺少必要参数

**修复**:
```python
i2v_embeds_node = NODE_CLASS_MAPPINGS['WanVideoImageToVideoEncode']()
image_embeds = i2v_embeds_node.process(
    vae=vae,
    width=width,
    height=height,
    num_frames=num_frames,
    force_offload=True,
    noise_aug_strength=0.0,
    start_latent_strength=1.0,
    end_latent_strength=1.0,
    start_image=img_tensor,
    end_image=None,
    add_cond_latents=None
)[0]
```

### 8. UI默认参数更新
**修改**:
- Frame Window Size: 77 → 117
- Motion Frame: 4 → 25
- Color Match: disabled → mkl
- FPS: 16 → 25

这些参数与InfiniteTalk工作流保持一致。

### 9. 视频转换修复
**问题**: 视频张量转换逻辑不正确
**修复**:
```python
if isinstance(video_tensor, torch.Tensor):
    # video_tensor shape: [frames, height, width, channels]
    video_array = (video_tensor.cpu().numpy() * 255).astype(np.uint8)
    print(f"[INFO] Video array shape: {video_array.shape}")
```

### 10. 进度回调支持
**新增**: 在所有关键步骤添加进度回调
- 0.05: Loading models
- 0.15: Loading VAE
- 0.25: Loading T5 encoder
- 0.35: Encoding text
- 0.45: Processing InfiniteTalk
- 0.55: Starting sampling
- 0.85: Decoding video
- 0.95: Converting to video

## 测试建议

### InfiniteTalk模式测试
1. 准备一张人物图片
2. 可选：准备一个音频文件
3. 使用以下参数：
   - Model: `wan\\infinitetalk\\Wan2_IceCannon2.1_InfiniteTalk.safetensors`
   - Frame Window Size: 117
   - Motion Frame: 25
   - Color Match: mkl
   - FPS: 25
   - Scheduler: 会自动使用multitalk

### WanAnimate模式测试
1. 准备参考图片
2. 可选：准备姿态图片和面部图片
3. 使用默认参数测试

### Standard I2V模式测试
1. 准备输入图片
2. 使用标准参数测试

## 已知问题和注意事项

1. **模型路径**: 确保模型文件位于正确的目录
   - InfiniteTalk模型: `models/diffusion_models/wan/infinitetalk/`
   - VAE: `models/vae/`
   - T5: `models/text_encoders/`
   - CLIP Vision: `models/clip_vision/`
   - Wav2Vec2: `models/wav2vec2/`

2. **内存管理**: InfiniteTalk模式需要较大显存，建议使用fp4或fp8量化

3. **音频格式**: 支持常见音频格式，会自动重采样到16kHz

4. **调度器**: InfiniteTalk模式会自动使用multitalk调度器，无需手动选择

## 文件修改清单

- `apps/wanvideo_gradio_app.py`: 主要修复文件
  - generate_image_to_video方法: 完全重写
  - UI参数: 更新默认值
  - 进度回调: 添加支持

## 参考节点

### InfiniteTalk工作流使用的节点
1. WanVideoModelLoader
2. WanVideoVAELoader
3. LoadWanVideoT5TextEncoder
4. WanVideoTextEncode
5. LoadCLIPVision
6. WanVideoClipVisionEncode
7. DownloadAndLoadWav2VecModel
8. MultiTalkWav2VecEmbeds
9. WanVideoImageToVideoMultiTalk
10. WanVideoSampler
11. WanVideoDecode

## 下一步

如果仍然遇到问题，请检查：
1. 控制台输出的错误信息
2. 模型文件是否存在
3. 依赖包是否正确安装
4. 显存是否足够

## 更新日志

- 2025-11-13: 初始修复，参考T2V和InfiniteTalk工作流
