# InfiniteTalk 最终修复方案

## 修复时间
2025-11-14 00:27

## 发现的问题

### 1. ❌ LoadCLIPVision节点不存在
**错误**: `'LoadCLIPVision'`
**原因**: 该节点在当前的ComfyUI-WanVideoWrapper中不存在
**解决**: 移除CLIP Vision相关代码，InfiniteTalk使用直接图像嵌入

### 2. ❌ Wav2Vec参数错误
**错误**: `DownloadAndLoadWav2VecModel.loadmodel() got an unexpected keyword argument 'model_name'`
**原因**: 
- 应该使用`Wav2VecModelLoader`而不是`DownloadAndLoadWav2VecModel`
- 参数应该是`model`而不是`model_name`
**解决**: 修改为正确的节点和参数

### 3. ⚠️ 采样器卡住
**现象**: 在"Loading transformer parameters to cuda: 100%"后卡住
**可能原因**: 
- multitalk调度器可能需要特定参数
- 显存不足
- 模型加载问题

## 已应用的修复

### 修复1: 移除CLIP Vision
```python
# 旧代码（错误）
clip_vision_loader = NODE_CLASS_MAPPINGS['LoadCLIPVision']()
clip_vision = clip_vision_loader.load_model(...)

# 新代码（正确）
# InfiniteTalk doesn't use CLIP Vision in the workflow
# It uses direct image embedding through the MultiTalk node
clip_embeds = None
print("[INFO] InfiniteTalk mode: using direct image embedding (no CLIP Vision needed)")
```

### 修复2: 修复Wav2Vec加载
```python
# 旧代码（错误）
wav2vec_loader = NODE_CLASS_MAPPINGS['DownloadAndLoadWav2VecModel']()
wav2vec_model = wav2vec_loader.loadmodel(
    model_name="TencentGameMate/chinese-wav2vec2-base",  # 错误参数名
    base_precision="fp16",
    load_device="main_device"
)[0]

# 新代码（正确）
wav2vec_loader = NODE_CLASS_MAPPINGS['Wav2VecModelLoader']()
# 自动查找models/wav2vec2/目录下的模型文件
wav2vec_models = glob.glob("models/wav2vec2/*.safetensors") + glob.glob("models/wav2vec2/*.bin")
if wav2vec_models:
    model_file = os.path.basename(wav2vec_models[0])
    wav2vec_model = wav2vec_loader.loadmodel(
        model=model_file,  # 正确参数名
        base_precision="fp16",
        load_device="main_device"
    )[0]
```

### 修复3: 添加采样器调试
```python
print(f"[DEBUG] Sampler args keys: {list(sampler_args.keys())}")
print(f"[DEBUG] Image embeds shape: {image_embeds[0].shape if isinstance(image_embeds, tuple) else 'N/A'}")

try:
    samples = sampler.process(**sampler_args)[0]
    print(f"[INFO] Sampling completed successfully")
except Exception as sample_error:
    print(f"[ERROR] Sampling failed: {sample_error}")
    traceback.print_exc()
    raise
```

## 需要的模型文件

### 必需文件
1. **Diffusion模型**: `models/diffusion_models/wan/infinitetalk/Wan2_IceCannon2.1_InfiniteTalk.safetensors`
2. **VAE**: `models/vae/ComfyUI-wan_2.1_vae.safetensors`
3. **T5编码器**: `models/text_encoders/models_t5_umt5-xxl-enc-fp8_fully_uncensored.safetensors`

### 可选文件（音频支持）
4. **Wav2Vec模型**: `models/wav2vec2/*.safetensors` 或 `*.bin`
   - 例如: `TencentGameMate_chinese-wav2vec2-base.safetensors`

## 下次运行时的日志

重新运行后，你应该看到：

```
[INFO] Text encoded successfully
[INFO] Processing input image...
[DEBUG] Image tensor shape: torch.Size([1, 480, 832, 3])
[INFO] Using InfiniteTalk mode...
[DEBUG] Loading WanVideoImageToVideoMultiTalk node...
[DEBUG] WanVideoImageToVideoMultiTalk node loaded
[INFO] InfiniteTalk mode: using direct image embedding (no CLIP Vision needed)
[DEBUG] Checking for audio file...
[INFO] Loading audio: ...
[DEBUG] Loading Wav2Vec model...
[DEBUG] Using Wav2Vec model: xxx.safetensors
[DEBUG] Wav2Vec model loaded
[DEBUG] Audio file loaded
[DEBUG] Creating audio embeds...
[INFO] Audio embeds created, actual frames: XXX
[DEBUG] Creating InfiniteTalk image embeds...
[INFO] InfiniteTalk embeds created successfully
[INFO] Starting sampling...
[DEBUG] Sampler args keys: ['model', 'image_embeds', 'shift', 'steps', 'cfg', 'seed', 'scheduler', 'riflex_freq_index', 'text_embeds', 'force_offload', 'multitalk_embeds']
[DEBUG] Image embeds shape: torch.Size([...])
Loading transformer parameters to cuda: 100%|...
[INFO] Sampling completed successfully  <-- 应该能看到这一行
[INFO] Decoding video...
```

## 如果仍然卡住

### 检查点1: 在"Loading transformer parameters"后卡住
**可能原因**:
1. 显存不足
2. multitalk调度器问题
3. 模型加载到GPU时出错

**解决方案**:
1. 检查显存使用: 打开任务管理器查看GPU内存
2. 尝试减小参数:
   - 分辨率: 832x480 → 640x360
   - 帧数: 81 → 49
   - Frame Window: 117 → 77
3. 尝试使用Standard I2V模式（不使用multitalk调度器）

### 检查点2: 如果显示错误
查看错误信息，可能是：
- 参数不匹配
- 模型文件损坏
- 显存不足

## 临时解决方案

### 方案A: 不使用音频
如果音频处理有问题，不上传音频文件，InfiniteTalk仍然可以工作（只是没有口型同步）。

### 方案B: 使用Standard I2V
Standard I2V模式更简单稳定：
```
Mode: Standard I2V
Steps: 20
Scheduler: unipc
CFG: 6.0
```

### 方案C: 减小参数
```
Width: 640
Height: 360
Frames: 49
Frame Window: 77
Motion Frame: 13
```

## 关键节点对照

| 功能 | 正确节点 | 错误节点 |
|------|----------|----------|
| Wav2Vec加载 | `Wav2VecModelLoader` | `DownloadAndLoadWav2VecModel` |
| Wav2Vec参数 | `model="xxx.safetensors"` | `model_name="xxx"` |
| CLIP Vision | 不需要 | `LoadCLIPVision` |
| 图像嵌入 | `WanVideoImageToVideoMultiTalk` | - |
| 音频嵌入 | `MultiTalkWav2VecEmbeds` | - |

## 下一步行动

1. **重新启动应用**
2. **测试InfiniteTalk（无音频）**
   - 不上传音频文件
   - 观察是否能通过采样阶段
3. **如果成功，测试InfiniteTalk（有音频）**
   - 确保Wav2Vec模型存在
   - 上传音频文件
4. **如果仍然卡住，提供完整日志**
   - 从"Starting Image to Video Generation"开始
   - 到卡住的位置
   - 包括所有[DEBUG]信息

## 预期结果

成功运行后，你应该能在`outputs/i2v/`目录下看到生成的视频文件：
- 文件名格式: `i2v_infinitetalk_YYYYMMDD_HHMMSS.mp4`
- 如果有音频，视频应该有口型同步效果
- 如果没有音频，视频仍然会生成，但没有口型同步
