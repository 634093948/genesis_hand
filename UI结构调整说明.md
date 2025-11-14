# 📐 UI 结构调整说明

**调整时间**: 2025/11/14 11:53
**调整内容**: Model Settings 集成到视频生成标签页

---

## 🔄 调整内容

### 之前的结构

```
WanVideo Genesis
├── 📹 视频生成 Video Generation
├── 🖼️ 图像生成 Image Generation
├── ⚙️ Model Settings ← 独立标签页
├── 🎨 LoRA
├── ⚡ Optimization
├── 📦 Presets
├── 📖 Scheduler Guide
└── ⚙️ Quantization & Attention
```

### 调整后的结构

```
WanVideo Genesis
│
├── 📹 视频生成 Video Generation ← 包含模型设置
│   ├── 🎬 生成模式选择
│   ├── 📷 输入图片 (动态)
│   ├── 📝 提示词
│   ├── 📐 图片处理 (动态)
│   ├── 📹 视频参数
│   ├── ⚙️ 生成参数
│   ├── 🎨 模型配置 (折叠) ← 集成在这里
│   │   ├── Diffusion Model
│   │   ├── VAE Model
│   │   └── T5 Text Encoder
│   ├── ⚙️ 高级设置 (折叠) ← 集成在这里
│   │   ├── Base Precision
│   │   ├── Quantization
│   │   └── Attention Mode
│   ├── 🎙️ InfiniteTalk 设置 (动态)
│   ├── 🎭 WanAnimate 设置 (动态)
│   └── 🎬 生成按钮
│
├── 🖼️ 图像生成 Image Generation
├── 🎨 LoRA
├── ⚡ Optimization
├── 📦 Presets
├── 📖 Scheduler Guide
└── ⚙️ Quantization & Attention
```

---

## ✅ 调整原因

### 1. 更符合逻辑
- 模型设置是视频生成的一部分
- 应该在生成视频时就能配置模型
- 不需要切换标签页

### 2. 简化操作流程
**之前**:
1. 切换到 Model Settings 标签页
2. 选择模型
3. 切换回视频生成标签页
4. 设置参数
5. 生成视频

**之后**:
1. 在视频生成标签页
2. 选择模型（折叠面板）
3. 设置参数
4. 生成视频

### 3. 减少标签页数量
- 从 8 个标签页减少到 7 个
- 界面更简洁
- 减少用户困惑

---

## 📊 模型配置位置

### 在视频生成标签页中

```
📹 视频生成
│
├── ... (其他参数)
│
├── 🎨 模型配置 ▼ (点击展开)
│   ├── Diffusion Model
│   │   └── [下拉选择]
│   ├── VAE Model
│   │   └── [下拉选择]
│   └── T5 Text Encoder
│       └── [下拉选择]
│
├── ⚙️ 高级设置 ▼ (点击展开)
│   ├── Base Precision
│   │   └── [下拉选择]
│   ├── Quantization
│   │   └── [下拉选择]
│   └── Attention Mode
│       └── [下拉选择]
│
└── ... (其他参数)
```

---

## 🎯 优势

### 1. 一站式操作
✅ 所有视频生成相关设置在一个地方
✅ 无需切换标签页
✅ 流程更顺畅

### 2. 默认折叠
✅ 不常用的设置默认折叠
✅ 界面更简洁
✅ 需要时再展开

### 3. 保持功能完整
✅ 所有模型配置功能都保留
✅ 所有高级设置都可用
✅ 只是位置调整

---

## 🔧 技术实现

### 隐藏旧的 Model Settings 标签页

```python
# Model Settings Tab (已集成到视频生成标签页，保留用于兼容)
with gr.Tab("Model Settings", visible=False):
    # 原有内容保留但不显示
    ...
```

### 在视频生成标签页中添加

```python
# Model configuration
with gr.Accordion("🎨 模型配置", open=False):
    model_name = gr.Dropdown(...)
    vae_name = gr.Dropdown(...)
    t5_model = gr.Dropdown(...)

# Advanced settings
with gr.Accordion("⚙️ 高级设置", open=False):
    base_precision = gr.Dropdown(...)
    quantization = gr.Dropdown(...)
    attention_mode = gr.Dropdown(...)
```

---

## 📝 注意事项

### 1. 变量名称
- 统一视频生成标签页中的变量: `model_name`, `vae_name`, `t5_model`
- 旧 Model Settings 标签页中的变量也是相同名称
- 使用统一视频生成标签页中的变量

### 2. 默认值
- 模型配置默认折叠 (`open=False`)
- 高级设置默认折叠 (`open=False`)
- 用户需要时可以展开

### 3. 兼容性
- 旧的 Model Settings 标签页保留但隐藏
- 如果有其他代码引用，不会报错
- 可以随时恢复显示

---

## 🎉 调整完成

### 现在的 UI 结构

```
📹 视频生成 (统一标签页)
├── 模式选择 ✅
├── 输入和参数 ✅
├── 模型配置 (折叠) ✅ 新位置
├── 高级设置 (折叠) ✅ 新位置
└── 生成按钮 ✅

其他标签页
├── 🖼️ 图像生成
├── 🎨 LoRA
├── ⚡ Optimization
├── 📦 Presets
├── 📖 Scheduler Guide
└── ⚙️ Quantization & Attention
```

**更简洁、更合理、更易用！** 🎊
