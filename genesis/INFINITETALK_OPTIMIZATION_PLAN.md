# InfiniteTalk 优化和修复方案

## 问题分析

### 问题1: 显存占用过大
- 当前实现一次性加载所有模型到GPU
- 没有使用模型offload机制
- 没有使用Sage Attention等优化

### 问题2: InfiniteTalk不工作，但普通I2V可以
- InfiniteTalk使用`multitalk_sampling`模式，需要特殊处理
- 当前实现可能缺少关键参数或配置

## ComfyUI InfiniteTalk工作流分析

### 关键节点配置

#### 1. WanVideoImageToVideoMultiTalk
```python
Widgets: [832, 480, 117, 25, False, 'mkl', False, 'infinitetalk', '']
参数对应:
- width: 832
- height: 480
- frame_window_size: 117
- motion_frame: 25
- force_offload: False
- colormatch: 'mkl'
- tiled_vae: False
- mode: 'infinitetalk'
- output_path: ''
```

#### 2. WanVideoSampler
```python
Widgets: [6, 1, 7, seed, 'randomize', False, 'dpm++_sde', ...]
参数对应:
- steps: 6
- cfg: 1
- shift: 7
- seed: random
- scheduler: 'dpm++_sde'
- force_offload: False
```

#### 3. MultiTalkWav2VecEmbeds
```python
Widgets: [True, 33, 25, 1, 1, 'para']
参数对应:
- normalize_loudness: True
- num_frames: 33 (注意：不是117！)
- fps: 25
- audio_scale: 1
- audio_cfg_scale: 1
- multi_audio_type: 'para'
```

#### 4. Wav2Vec模型加载
```python
Node: DownloadAndLoadWav2VecModel (不是Wav2VecModelLoader!)
Widgets: ['TencentGameMate/chinese-wav2vec2-base', 'fp16', 'main_device']
```

### 关键发现

1. **音频帧数不匹配**: ComfyUI使用`num_frames=33`，而不是`frame_window_size=117`
2. **使用DownloadAndLoadWav2VecModel**: 不是`Wav2VecModelLoader`
3. **使用ClipVisionEncode**: ComfyUI确实使用了CLIP Vision编码
4. **force_offload=False**: 在节点级别没有启用offload

## 优化方案

### 方案1: 显存优化 - Sage Attention

#### 1.1 检查Sage Attention支持
```python
# 在wanvideo_gradio_app.py开头添加
try:
    import sageattention
    SAGE_ATTENTION_AVAILABLE = True
    print("[INFO] Sage Attention available for memory optimization")
except ImportError:
    SAGE_ATTENTION_AVAILABLE = False
    print("[INFO] Sage Attention not available, using standard attention")
```

#### 1.2 启用模型offload
```python
# 在模型加载时
model_loader = NODE_CLASS_MAPPINGS['WanVideoModelLoader']()
model = model_loader.load_model(
    model_name=model_name,
    base_precision="fp8_e4m3fn",  # 使用FP8降低显存
    load_device="main_device",
    auto_cpu_offload=True,  # 启用CPU offload
    compile_args=None
)[0]
```

#### 1.3 启用VAE tiling
```python
# 在图像编码时
image_embeds = multitalk_i2v_node.process(
    vae=vae,
    ...
    tiled_vae=True,  # 启用VAE分块处理
    force_offload=True,  # 启用强制offload
    ...
)
```

#### 1.4 使用梯度检查点
```python
# 在采样器调用时
sampler_args = {
    ...
    "force_offload": True,  # 启用offload
    "use_tf32": True,  # 使用TF32加速
    "force_contiguous_tensors": True,  # 优化内存布局
}
```

### 方案2: 修复InfiniteTalk

#### 2.1 修复Wav2Vec模型加载
```python
# 使用正确的节点
wav2vec_loader = NODE_CLASS_MAPPINGS['DownloadAndLoadWav2VecModel']()
wav2vec_model = wav2vec_loader.loadmodel(
    model="TencentGameMate/chinese-wav2vec2-base",  # 完整模型名
    base_precision="fp16",
    load_device="main_device"
)[0]
```

#### 2.2 修复音频帧数计算
```python
# 音频帧数应该基于实际音频长度，不是frame_window_size
# ComfyUI使用33帧，这是基于音频时长计算的
audio_embeds_result = wav2vec_embeds_node.process(
    wav2vec_model=wav2vec_model,
    audio_1=audio_data,
    normalize_loudness=True,
    num_frames=frame_window_size,  # 保持与图像一致
    fps=fps,
    audio_scale=1.0,
    audio_cfg_scale=1.0,
    multi_audio_type="para"
)
```

#### 2.3 添加CLIP Vision编码（如果需要）
```python
# ComfyUI确实使用了WanVideoClipVisionEncode
# 但在InfiniteTalk模式下可能是可选的
try:
    clip_vision_loader = NODE_CLASS_MAPPINGS['LoadCLIPVision']()
    clip_vision = clip_vision_loader.load_model(
        clip_name="sigclip_vision_patch14_384.safetensors"
    )[0]
    
    clip_encode_node = NODE_CLASS_MAPPINGS['WanVideoClipVisionEncode']()
    clip_embeds = clip_encode_node.encode(
        clip_vision=clip_vision,
        image=img_tensor
    )[0]
except Exception as e:
    print(f"[WARNING] CLIP Vision encoding failed: {e}")
    clip_embeds = None
```

#### 2.4 确保正确的参数传递
```python
# 采样器参数必须完全匹配ComfyUI
sampler_args = {
    "model": model,
    "image_embeds": image_embeds,
    "shift": shift,
    "steps": steps,
    "cfg": cfg,
    "seed": seed,
    "scheduler": scheduler,
    "riflex_freq_index": 0,
    "text_embeds": text_embeds,
    "force_offload": True,
    "multitalk_embeds": audio_embeds,  # 关键！
    "denoise_strength": denoise_strength,
    "batched_cfg": False,
    "rope_function": "default",
    "start_step": 0,
    "end_step": -1,
    "add_noise_to_samples": False
}
```

## 实施优先级

### 高优先级（立即修复）
1. ✅ 修复Wav2Vec模型加载方式
2. ✅ 确保multitalk_embeds正确传递
3. ✅ 验证image_embeds结构正确

### 中优先级（显存优化）
4. ⚠️ 启用force_offload
5. ⚠️ 启用tiled_vae
6. ⚠️ 使用FP8精度

### 低优先级（高级优化）
7. 🔄 集成Sage Attention
8. 🔄 使用TF32
9. 🔄 优化内存布局

## 测试步骤

### 步骤1: 基础功能测试
```
Mode: InfiniteTalk
Steps: 6
CFG: 1
Shift: 7
Scheduler: dpm++_sde
Frame Window: 117
Motion Frame: 25
Audio: 不上传
```

### 步骤2: 音频功能测试
```
Mode: InfiniteTalk
Steps: 6
CFG: 1
Shift: 7
Scheduler: dpm++_sde
Frame Window: 117
Motion Frame: 25
Audio: 上传短音频（<5秒）
```

### 步骤3: 显存优化测试
```
启用所有优化选项
监控显存使用
对比优化前后的显存占用
```

## 预期改进

### 显存优化
- **当前**: ~24GB (满载)
- **优化后**: ~16GB (offload + tiling)
- **高级优化**: ~12GB (FP8 + Sage Attention)

### InfiniteTalk功能
- **当前**: 不工作（NoneType错误）
- **修复后**: 正常生成视频
- **带音频**: 口型同步效果

## 下一步行动

1. **立即修复**: 更新Wav2Vec加载逻辑
2. **验证参数**: 确保所有参数与ComfyUI一致
3. **启用优化**: 逐步启用显存优化选项
4. **测试验证**: 完整测试流程
