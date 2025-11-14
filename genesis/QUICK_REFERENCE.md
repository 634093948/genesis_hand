# InfiniteTalk 快速参考

## 🚀 立即测试

### 1. 重启应用
```bash
Ctrl+C  # 停止当前应用
python genesis/apps/wanvideo_gradio_app.py  # 重新启动
```

### 2. 推荐配置（无音频）
```
Mode: InfiniteTalk
Steps: 20
CFG: 6.0
Shift: 5.0
Scheduler: dpm++_sde
Width: 832
Height: 480
Frame Window: 117
Motion Frame: 25
FPS: 25
Audio: 不上传
```

### 3. 预期日志
```
[INFO] Sage Attention available - memory optimization enabled
[DEBUG] Memory optimizations: tiled_vae=True, force_offload=True
[DEBUG] MultiTalk node result type: <class 'tuple'>
[DEBUG] Image embeds type: <class 'dict'>
[DEBUG] multitalk_sampling: True
[INFO] InfiniteTalk mode without audio (multitalk_embeds=None)
[INFO] Starting sampling...
[INFO] Sampling completed successfully
```

## 📊 显存使用

| 配置 | 显存占用 | 适用GPU |
|------|----------|---------|
| 优化前 | ~24GB | RTX 4090, A6000 |
| 优化后 | ~17GB | RTX 4080, 3090 |
| 降低分辨率 | ~12GB | RTX 4070 Ti, 3080 |
| FP8模型 | ~8GB | RTX 3060, 4060 |

## ⚙️ 优化开关

当前默认配置（在代码中）:
```python
use_tiled_vae = True        # VAE分块处理
use_force_offload = True    # 模型自动卸载
use_tf32 = True             # TF32加速
force_contiguous_tensors = True  # 内存优化
```

### 如果显存充足（>24GB）
修改代码:
```python
use_tiled_vae = False       # 关闭tiling，更快
use_force_offload = False   # 关闭offload，更快
```

### 如果显存不足（<16GB）
降低参数:
```
Width: 640
Height: 360
Frame Window: 77
Steps: 10
```

## 🐛 常见问题

### Q1: 仍然报NoneType错误
**检查**: 日志中是否有 `[DEBUG] multitalk_sampling: True`
**如果没有**: 说明image_embeds创建失败，查看之前的错误

### Q2: 显存不足OOM
**解决**: 
1. 降低分辨率
2. 减少帧数
3. 使用更小的步数

### Q3: 生成速度很慢
**原因**: force_offload会增加模型加载时间
**解决**: 如果显存够用，关闭offload

### Q4: 没有看到Sage Attention消息
**说明**: 未安装Sage Attention（可选）
**安装**: `pip install sageattention`

## 📝 调试清单

如果出错，检查这些日志:
- [ ] `[INFO] Sage Attention available` (可选)
- [ ] `[DEBUG] Memory optimizations: tiled_vae=True`
- [ ] `[DEBUG] MultiTalk node result type: <class 'tuple'>`
- [ ] `[DEBUG] Image embeds type: <class 'dict'>`
- [ ] `[DEBUG] multitalk_sampling: True`
- [ ] `[INFO] InfiniteTalk mode without audio`
- [ ] `[INFO] Starting sampling...`
- [ ] `[INFO] Sampling completed successfully`

## 🎯 下一步

1. **测试无音频**: 确保基础功能正常
2. **测试有音频**: 需要先下载Wav2Vec模型
3. **优化参数**: 根据显存调整配置
4. **安装Sage Attention**: 进一步优化（可选）

## 📚 相关文档

- `INFINITETALK_FIXES_APPLIED.md` - 详细修复说明
- `INFINITETALK_OPTIMIZATION_PLAN.md` - 优化方案
- `WAV2VEC_MODEL_GUIDE.md` - 音频模型下载
- `SCHEDULER_ERROR_FIX.md` - 调度器问题
