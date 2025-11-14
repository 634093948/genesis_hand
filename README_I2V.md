# WanVideo Genesis v3.0 - Image to Video 功能说明

## 🎉 重大更新

WanVideo Genesis v3.0 新增了完整的**图生视频 (Image to Video)** 功能,支持三种专业模式:

- **Standard I2V** - 标准图生视频
- **InfiniteTalk** - 长视频生成,支持音频驱动
- **WanAnimate** - 高级动画生成,支持姿态和面部控制

---

## 🚀 快速开始

### 1. 启动应用

```bash
VIDEO.bat
```

### 2. 切换到图生视频标签页

打开浏览器后,点击 **"🖼️ Image to Video"** 标签页

### 3. 选择模式并生成

1. 选择 I2V 模式 (Standard I2V / InfiniteTalk / WanAnimate)
2. 上传输入图片
3. 输入提示词 (可选)
4. 调整参数
5. 点击 **"🎬 Generate Video"**

---

## 📖 三种模式详解

### Standard I2V (标准模式)

**适用场景:** 通用图片转视频

**特点:**
- ✅ 最简单易用
- ✅ 速度快
- ✅ 支持任意图片
- ✅ 适合快速测试

**推荐配置:**
```
Resolution: 832x480
Frames: 81
Steps: 30
CFG: 6.0
Scheduler: unipc
```

---

### InfiniteTalk (长视频模式)

**适用场景:** 人物说话视频,长视频生成

**特点:**
- ✅ 支持音频驱动
- ✅ 窗口化生成
- ✅ 可生成超长视频
- ✅ 适合对话场景

**推荐配置:**
```
Resolution: 832x480
Frames: 161+
Frame Window: 77
Motion Frame: 4
Steps: 30
CFG: 6.0
Scheduler: res_2m
```

**所需模型:**
- Wan2_1-InfiniteTalk-Single_fp16.safetensors
- Wan2_1-InfiniteTalk-Multi_fp16.safetensors

---

### WanAnimate (高级动画模式)

**适用场景:** 高质量动画,精确控制

**特点:**
- ✅ 支持姿态控制
- ✅ 支持面部控制
- ✅ 窗口颜色匹配
- ✅ 最高质量输出

**推荐配置:**
```
Resolution: 832x480
Frames: 81
Frame Window: 77
Pose Strength: 1.0
Face Strength: 1.0
Steps: 30
CFG: 7.0
Scheduler: res_5s
```

**所需模型:**
- wan2.2_animate_ED_BF16+FP8_V3.1.safetensors
- wan2.2_animate_bf16_with_fp8_e4m3fn_scaled_ED.safetensors

---

## 🎯 使用示例

### 示例 1: 风景照片变视频

**模式:** Standard I2V

**输入:**
- 图片: 一张风景照片
- 提示词: "Camera slowly panning across the beautiful landscape"

**输出:** 带有镜头运动的风景视频

---

### 示例 2: 人物说话视频

**模式:** InfiniteTalk

**输入:**
- 图片: 人物正面照
- 音频: 说话的音频文件 (可选)
- 提示词: "A person talking naturally with expressions"

**输出:** 人物说话的视频,嘴型与音频同步

---

### 示例 3: 精确控制的动画

**模式:** WanAnimate

**输入:**
- 参考图片: 角色图片
- 姿态图片: 目标姿态 (可选)
- 面部图片: 目标表情 (可选)
- 提示词: "Smooth animation with natural movements"

**输出:** 高质量动画,精确控制姿态和表情

---

## ⚙️ 高级设置

### 量化设置 (减少显存)

**RTX 4090/4080:**
```
Base Precision: bf16
Quantization: fp8_e4m3fn_fast
Attention: sageattn_3_fp8
```

**RTX 3090/3080:**
```
Base Precision: bf16
Quantization: fp8_e5m2
Attention: sageattn
```

### 采样器选择

**快速生成:**
- unipc (推荐)
- res_2m
- euler

**高质量:**
- res_5s (推荐)
- gauss-legendre_5s
- iching/wuxing-stable

---

## 📊 性能对比

| 模式 | 速度 | 质量 | 显存 | 长度限制 |
|------|------|------|------|----------|
| Standard I2V | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 241帧 |
| InfiniteTalk | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | 无限制 |
| WanAnimate | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | 241帧 |

---

## 💡 使用技巧

### 1. 提高生成质量
- 使用高质量输入图片
- 增加 Steps 数量 (30-50)
- 使用高质量采样器 (res_5s)
- 调整 CFG 和 Shift 参数

### 2. 减少显存占用
- 启用量化 (fp8)
- 降低分辨率
- 减少帧数
- 使用 Standard I2V 模式

### 3. 加快生成速度
- 使用快速采样器 (unipc)
- 减少 Steps (20-30)
- 启用 fp8_fast 量化
- 使用 Standard I2V 模式

---

## ⚠️ 常见问题

### Q: 需要什么样的输入图片?

**A:** 
- **分辨率:** 推荐 832x480 或更高
- **格式:** JPG, PNG, WebP
- **InfiniteTalk:** 建议使用人物正面照,面部清晰
- **WanAnimate:** 建议提供清晰的参考图

### Q: InfiniteTalk 人物不说话?

**A:**
1. 确保使用 InfiniteTalk 专用模型
2. 上传音频文件
3. 检查 Motion Frame 设置
4. 在提示词中描述说话动作

### Q: 显存不足怎么办?

**A:**
1. 降低分辨率 (640x384)
2. 减少帧数
3. 启用量化 (fp8)
4. 使用 Standard I2V 模式

---

## 📁 输出文件

**保存位置:**
```
outputs/i2v/
```

**文件命名格式:**
```
i2v_standard_20251113_213045.mp4
i2v_infinitetalk_20251113_213145.mp4
i2v_wananimate_20251113_213245.mp4
```

---

## 📚 相关文档

- **图生视频使用指南.txt** - 详细的使用教程
- **v3.0新功能总结.txt** - 新功能总结
- **快速配置参考.txt** - 快速配置参考
- **更新日志.txt** - 版本更新历史

---

## 🎓 技术特性

- ✅ 自动图片预处理和缩放
- ✅ 支持 PIL Image 和 Tensor 输入
- ✅ 完整的错误处理和日志
- ✅ 进度条显示
- ✅ 帧预览功能
- ✅ 元数据导出
- ✅ 支持所有采样器 (97+种)
- ✅ 支持所有量化模式
- ✅ 支持所有注意力模式

---

## 🎉 总结

WanVideo Genesis v3.0 带来了完整的图生视频功能,让您可以:

- 🖼️ 将静态图片转换为动态视频
- 🗣️ 生成人物说话的长视频
- 🎨 创建高质量的精确控制动画

**立即体验,开启图生视频的新时代!** 🚀

---

## 📞 技术支持

遇到问题?
1. 查看控制台日志
2. 检查模型是否正确
3. 确认输入图片格式
4. 参考文档和示例配置

---

**WanVideo Genesis v3.0** - Powered by Genesis Core & ComfyUI-WanVideoWrapper
