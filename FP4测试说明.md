# 🚀 FP4 量化测试说明

**测试时间**: 2025/11/14 13:35
**目的**: 测试 sageattn_3_fp4 注意力模式和 fp4 量化

---

## 📋 测试配置

### 基本参数

| 参数 | 值 | 说明 |
|------|-----|------|
| **模式** | InfiniteTalk | 图生视频 |
| **输入图片** | `D:\rh推广项目\工作流及图形\1ecf8fdfbb57ef8ebb1cbec5973d5cc732c1a12cda6b2e71ac46a1aa4af40548.jpg` | 测试图片 |
| **分辨率** | 640x720 | 宽x高 |
| **帧数** | 81 | 总帧数 |
| **FPS** | 16 | 帧率 |
| **时长** | ~5 秒 | 81帧 / 16fps |

### 生成参数

| 参数 | 值 | 说明 |
|------|-----|------|
| **Steps** | 6 | 采样步数 |
| **CFG** | 7.0 | 引导强度 |
| **Shift** | 7 | 时间偏移 |
| **Scheduler** | euler | 调度器 |
| **Denoise** | 1.0 | 去噪强度 |

### 优化参数

| 参数 | 值 | 说明 |
|------|-----|------|
| **Quantization** | fp4_experimental | FP4 量化 |
| **Attention Mode** | sageattn_3_fp4 | FP4 注意力 |
| **Blocks to Swap** | 40 | 块交换数量 |
| **Auto Hardware Tuning** | True | 自动硬件调优 |
| **VRAM Threshold** | 50% | VRAM 阈值 |

---

## 🔬 FP4 实现说明

### 参考实现

从 `ComfyUI-WanVideoWrapper` 复刻的实现：

1. **量化选项**:
   - `fp4_experimental` - FP4 实验模式
   - `fp4_scaled` - FP4 缩放模式
   - `fp4_scaled_fast` - FP4 快速缩放模式

2. **注意力模式**:
   - `sageattn_3_fp4` - FP4 微缩放注意力（RTX 5090 优化）

### 工作原理

**FP4 量化**:
```python
# 权重使用 FP8 格式（PyTorch 不支持 FP4 权重存储）
# FP4 加速发生在注意力层
convert_fp4_linear(transformer, base_dtype, params_to_keep)
```

**FP4 注意力**:
- 使用 FP4 微缩放进行注意力计算
- 针对 RTX 5090 优化（1038 TOPS）
- 比 FP8 更快，内存占用更少

---

## 📊 预期性能

### RTX 5090 (1038 TOPS)

| 指标 | 预期值 |
|------|--------|
| **生成速度** | 极快 |
| **VRAM 使用** | 极低 |
| **质量** | 高 |

### 其他显卡

| 显卡 | FP4 支持 | 建议 |
|------|----------|------|
| **RTX 5090** | ✅ 完全支持 | 推荐使用 |
| **RTX 4090** | ⚠️ 部分支持 | 可尝试 |
| **RTX 4080** | ⚠️ 部分支持 | 可尝试 |
| **RTX 3090** | ❌ 不支持 | 使用 FP8 |

---

## 🔍 测试脚本

### 运行测试

```bash
python test_infinitetalk_fp4.py
```

### 脚本功能

1. ✅ 加载测试图片
2. ✅ 初始化 WanVideoWorkflow
3. ✅ 配置 FP4 参数
4. ✅ 生成视频
5. ✅ 显示进度
6. ✅ 保存结果

---

## 📝 测试检查点

### 启动阶段

- [ ] 图片加载成功
- [ ] Workflow 初始化成功
- [ ] 模型缓存系统启动

### 模型加载阶段

- [ ] Diffusion Model 加载（使用缓存）
- [ ] VAE 加载（使用缓存）
- [ ] T5 加载（使用缓存）
- [ ] FP4 量化应用成功

### 生成阶段

- [ ] 文本编码完成
- [ ] 图片处理完成
- [ ] InfiniteTalk 模式启动
- [ ] 静默音频嵌入加载
- [ ] 采样开始
- [ ] 进度正常显示

### 完成阶段

- [ ] 视频生成成功
- [ ] 文件保存成功
- [ ] 元数据正确

---

## ⚠️ 可能的问题

### 1. FP4 不支持

**错误**: "FP4 not supported on this GPU"

**解决**:
- 检查显卡型号
- 降级到 FP8: `quantization="fp8_e4m3fn_fast"`
- 降级注意力: `attention_mode="sageattn_3_fp8"`

### 2. VRAM 不足

**错误**: "CUDA out of memory"

**解决**:
- 增加块交换: `blocks_to_swap=60`
- 降低分辨率: `width=512, height=576`
- 减少帧数: `num_frames=61`

### 3. 模型未找到

**错误**: "Model not found"

**解决**:
- 检查模型文件是否存在
- 检查 MelBandRoformer 是否设置
- 运行 `SETUP_MELBAND.bat`

---

## 📈 性能对比

### FP4 vs FP8 vs FP16

| 模式 | 速度 | VRAM | 质量 |
|------|------|------|------|
| **FP4** | 最快 | 最低 | 高 |
| **FP8** | 快 | 低 | 高 |
| **FP16** | 中等 | 中等 | 最高 |
| **BF16** | 中等 | 中等 | 最高 |

### 注意力模式对比

| 模式 | 速度 | VRAM | 硬件要求 |
|------|------|------|----------|
| **sageattn_3_fp4** | 最快 | 最低 | RTX 5090 |
| **sageattn_3_fp8** | 很快 | 低 | RTX 4000+ |
| **sageattn_3** | 快 | 中等 | RTX 3000+ |
| **sageattn** | 中等 | 中等 | RTX 2000+ |
| **flash_attn_3** | 快 | 低 | RTX 3000+ |
| **sdpa** | 慢 | 高 | 通用 |

---

## 🎯 测试目标

### 主要目标

1. ✅ 验证 FP4 量化正常工作
2. ✅ 验证 sageattn_3_fp4 注意力正常工作
3. ✅ 验证模型缓存机制有效
4. ✅ 验证 81 帧生成稳定
5. ✅ 验证 640x720 分辨率正常

### 次要目标

1. 测量生成时间
2. 测量 VRAM 使用
3. 评估视频质量
4. 检查缓存效果

---

## 📊 预期结果

### 第一次生成

```
[LOAD] Loading model... (5-10 秒)
[CACHE] Model cached ✅
[LOAD] Loading VAE... (2-3 秒)
[CACHE] VAE cached ✅
[LOAD] Loading T5... (3-5 秒)
[CACHE] T5 cached ✅
[INFO] FP4 quantization mode enabled
[INFO] Using sageattn_3_fp4 attention
[生成] 81 帧, 640x720, 6 步
总时间: 约 30-50 秒
```

### 第二次生成（如果测试）

```
[CACHE] Using cached model ✅ (0.1 秒)
[CACHE] Using cached VAE ✅ (0.1 秒)
[CACHE] Using cached T5 ✅ (0.1 秒)
[INFO] FP4 quantization mode enabled
[INFO] Using sageattn_3_fp4 attention
[生成] 81 帧, 640x720, 6 步
总时间: 约 20-35 秒 (快 30-40%)
```

---

## 🎉 成功标准

测试通过需要满足:

1. ✅ 视频生成成功
2. ✅ 无错误或崩溃
3. ✅ 视频质量良好
4. ✅ VRAM 使用合理
5. ✅ 生成时间合理

---

**测试正在运行中，请查看终端窗口查看进度！** 🚀
