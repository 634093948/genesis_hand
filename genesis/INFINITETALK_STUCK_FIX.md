# InfiniteTalk卡住问题诊断和修复

## 问题现象
程序在文本编码后卡住，没有进一步输出。

## 已应用的修复

### 1. 添加详细调试信息
现在会显示每个步骤的进度：
- `[DEBUG] Image tensor shape`
- `[DEBUG] Loading WanVideoImageToVideoMultiTalk node...`
- `[DEBUG] Loading CLIP Vision model...`
- `[DEBUG] CLIP Vision loader created`
- 等等...

### 2. 添加超时保护
CLIP Vision加载现在有30秒超时限制，如果超时会跳过并继续。

### 3. 允许无CLIP Vision运行
如果CLIP Vision加载失败，程序会继续运行（可能影响质量但不会卡住）。

## 下次运行时查看的关键日志

重新运行后，请注意以下日志：

```
[INFO] Text encoded successfully
[INFO] Processing input image...
[DEBUG] Image tensor shape: torch.Size([...])
[INFO] Using InfiniteTalk mode...
[DEBUG] Loading WanVideoImageToVideoMultiTalk node...
[DEBUG] WanVideoImageToVideoMultiTalk node loaded
[DEBUG] Loading CLIP Vision model...
[DEBUG] CLIP Vision loader created
```

### 如果卡在"Loading CLIP Vision model..."
这说明CLIP Vision模型加载有问题。可能原因：
1. 模型文件不存在或路径错误
2. 模型文件损坏
3. 显存不足

### 如果显示"CLIP Vision loading timeout"
说明加载超时（30秒），程序会自动跳过CLIP Vision继续运行。

### 如果显示"Failed to load/encode CLIP Vision"
说明CLIP Vision加载失败，程序会继续运行但不使用CLIP embeds。

## 可能的卡住位置

### 位置1: CLIP Vision加载
**日志**: 卡在 `[DEBUG] Loading CLIP Vision model...` 之后
**原因**: CLIP Vision模型加载卡住
**解决**: 
- 现在有30秒超时，会自动跳过
- 检查模型文件: `models/clip_vision/sigclip_vision_patch14_384.safetensors`

### 位置2: CLIP Vision编码
**日志**: 卡在 `[DEBUG] Encoding image with CLIP Vision...` 之后
**原因**: 图像编码过程卡住
**解决**: 
- 检查图像尺寸是否合理
- 检查显存是否足够

### 位置3: 音频处理
**日志**: 卡在 `[DEBUG] Loading Wav2Vec model...` 之后
**原因**: Wav2Vec模型加载或音频处理卡住
**解决**: 
- 如果不需要音频，不要上传音频文件
- 检查音频文件格式是否支持

### 位置4: InfiniteTalk embeds创建
**日志**: 卡在 `[DEBUG] Creating InfiniteTalk image embeds...` 之后
**原因**: MultiTalk节点处理卡住
**解决**: 
- 检查VAE是否正确加载
- 检查显存是否足够
- 尝试减小分辨率或帧数

## 临时解决方案

如果InfiniteTalk一直卡住，可以尝试：

### 方案1: 使用Standard I2V模式
Standard I2V模式不需要CLIP Vision和音频处理，更简单稳定。

### 方案2: 减小参数
- 降低分辨率: 832x480 → 640x360
- 减少帧数: 81 → 49
- 减小Frame Window: 117 → 77

### 方案3: 检查模型文件
确保以下模型文件存在：
- `models/clip_vision/sigclip_vision_patch14_384.safetensors`
- `models/diffusion_models/wan/infinitetalk/Wan2_IceCannon2.1_InfiniteTalk.safetensors`
- `models/vae/ComfyUI-wan_2.1_vae.safetensors`

## 推荐测试步骤

### 步骤1: 测试Standard I2V
先测试Standard I2V模式，确保基本功能正常：
```
Mode: Standard I2V
Steps: 20
Scheduler: unipc
```

### 步骤2: 测试InfiniteTalk（无音频）
不上传音频文件，测试InfiniteTalk基本功能：
```
Mode: InfiniteTalk
Audio: 不上传
Frame Window: 117
Motion Frame: 25
```

### 步骤3: 测试InfiniteTalk（有音频）
上传音频文件，测试完整功能：
```
Mode: InfiniteTalk
Audio: 上传音频文件
Frame Window: 117
Motion Frame: 25
```

## 日志分析

### 正常流程应该看到：
```
[INFO] Text encoded successfully
[INFO] Processing input image...
[DEBUG] Image tensor shape: torch.Size([1, 480, 832, 3])
[INFO] Using InfiniteTalk mode...
[DEBUG] Loading WanVideoImageToVideoMultiTalk node...
[DEBUG] WanVideoImageToVideoMultiTalk node loaded
[DEBUG] Loading CLIP Vision model...
[DEBUG] CLIP Vision loader created
[DEBUG] CLIP Vision model loaded successfully
[DEBUG] Encoding image with CLIP Vision...
[DEBUG] CLIP Vision encoder created
[INFO] CLIP embeds created successfully
[DEBUG] Checking for audio file...
[DEBUG] No audio file provided, skipping audio processing
[DEBUG] Creating InfiniteTalk image embeds...
[DEBUG] Parameters: width=832, height=480, frame_window=117, motion_frame=25
[INFO] InfiniteTalk embeds created successfully with frame_window=117, motion_frame=25
[INFO] Starting sampling...
[DEBUG] Steps requested: 6
...
```

### 如果卡住，最后一行会停在某个[DEBUG]消息

## 下一步

1. **重新运行应用**
2. **观察新的调试日志**
3. **记录卡在哪一行**
4. **如果30秒后仍卡住，手动停止并报告最后一行日志**

## 备注

- CLIP Vision是可选的，没有它也能运行（但质量可能下降）
- 音频也是可选的，没有音频也能运行
- 如果一直有问题，建议先使用Standard I2V模式
