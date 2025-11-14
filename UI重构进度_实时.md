# 🎨 UI 重构进度 - 实时更新

**开始时间**: 2025/11/14 11:39
**备份文件**: `wanvideo_gradio_app.py.before_ui_refactor_20251114_113958`

---

## ✅ 已完成 (5/10)

### 1. ✅ 重命名主标签页
- 将 "Generation" 改为 "📹 视频生成 Video Generation"
- 添加统一视频生成平台说明

### 2. ✅ 添加模式选择
- 创建 `video_gen_mode` Radio 组件
- 选项: 文生视频 / InfiniteTalk / WanAnimate / Standard I2V

### 3. ✅ 添加图片输入组
- 创建 `image_input_group` (默认隐藏)
- 包含图片上传组件

### 4. ✅ 添加图片处理参数组
- 创建 `image_processing_group` (默认隐藏)
- 包含: keep_proportion, crop_position, upscale_method

### 5. ✅ 添加模式特定设置
- 创建 `infinitetalk_group` (默认隐藏)
  - 音频文件
  - 窗口参数
  - Wav2Vec 设置
- 创建 `wananimate_group` (默认隐藏)
  - 姿态图片
  - 面部图片
  - 强度设置

### 6. ✅ 实现动态显示逻辑
- 创建 `update_video_gen_mode_visibility` 函数
- 绑定模式切换事件

### 7. ✅ 添加图像生成预留板块
- 创建新标签页 "🖼️ 图像生成 Image Generation"
- 添加功能说明和开发中提示

---

## 🔄 进行中 (当前)

### 8. 🔄 优化参数布局
- 使用 Accordion 折叠不常用设置
- 使用 Row 横向排列参数
- 优化视觉层次

---

## ⏳ 待完成 (2/10)

### 9. ⏳ 连接生成函数
- 更新按钮事件绑定
- 根据模式调用不同的生成函数
- 参数映射和传递

### 10. ⏳ 清理旧代码
- 删除或隐藏旧的图生视频标签页
- 清理重复代码
- 更新注释

---

## 📊 新的 UI 结构

```
WanVideo Genesis
│
├── 📹 视频生成 Video Generation ✅ 新建
│   ├── 🎬 生成模式选择 ✅
│   │   ├── 文生视频 Text to Video
│   │   ├── 图生视频 - InfiniteTalk
│   │   ├── 图生视频 - WanAnimate
│   │   └── 图生视频 - Standard I2V
│   │
│   ├── 输入图片 ✅ (动态显示)
│   ├── 提示词 ✅
│   ├── 📐 图片处理 ✅ (动态显示)
│   ├── 📹 视频参数 ✅
│   ├── ⚙️ 生成参数 ✅
│   ├── 🎙️ InfiniteTalk 设置 ✅ (动态显示)
│   ├── 🎭 WanAnimate 设置 ✅ (动态显示)
│   └── 🎬 生成按钮 ✅
│
├── 🖼️ 图像生成 Image Generation ✅ 新建
│   └── 功能开发中...
│
├── 🖼️ Image to Video (旧版) ⚠️ 保留
│   └── (原有功能保持不变)
│
├── ⚙️ Model Settings
├── 🎨 LoRA
├── ⚡ Optimization
├── 📦 Presets
├── 📖 Scheduler Guide
└── ⚙️ Quantization & Attention
```

---

## 🎯 动态显示规则

| 组件 | 文生视频 | InfiniteTalk | WanAnimate | Standard I2V |
|------|---------|-------------|-----------|-------------|
| 输入图片 | ❌ | ✅ | ✅ | ✅ |
| 图片处理 | ❌ | ✅ | ✅ | ✅ |
| InfiniteTalk 设置 | ❌ | ✅ | ❌ | ❌ |
| WanAnimate 设置 | ❌ | ❌ | ✅ | ❌ |

---

## 🔧 技术细节

### 组件变量名

**统一视频生成标签页**:
- `video_gen_mode` - 模式选择
- `image_input_group` - 图片输入组
- `input_image` - 输入图片
- `image_processing_group` - 图片处理组
- `keep_proportion` - 适配方式
- `crop_position` - 裁剪位置
- `upscale_method` - 缩放算法
- `infinitetalk_group` - InfiniteTalk 设置组
- `audio_file` - 音频文件
- `frame_window_size` - 窗口大小
- `motion_frame` - 运动帧
- `wav2vec_precision` - Wav2Vec 精度
- `wav2vec_device` - Wav2Vec 设备
- `wananimate_group` - WanAnimate 设置组
- `pose_images` - 姿态图片
- `face_images` - 面部图片
- `pose_strength` - 姿态强度
- `face_strength` - 面部强度
- `colormatch` - 颜色匹配

**共通参数** (所有模式):
- `positive_prompt` - 正向提示词
- `negative_prompt` - 负向提示词
- `width` - 宽度
- `height` - 高度
- `num_frames` - 帧数
- `fps` - 帧率
- `steps` - 步数
- `cfg` - CFG Scale
- `shift` - Shift
- `seed` - 种子
- `scheduler` - 采样器
- `denoise_strength` - 去噪强度

---

## 📝 下一步操作

### 立即执行:
1. 优化参数布局（使用 Accordion）
2. 连接生成函数
3. 测试所有模式

### 后续优化:
1. 添加模型配置组
2. 添加高级设置折叠面板
3. 优化视觉效果

---

## ⚠️ 注意事项

1. **保持兼容性**: 旧的图生视频标签页暂时保留
2. **参数名称**: 新标签页使用新的变量名，避免冲突
3. **测试充分**: 每个模式都需要测试

---

**当前进度**: 50% (5/10) ✅
**预计完成**: 继续进行中...
