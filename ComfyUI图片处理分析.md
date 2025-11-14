# 📸 ComfyUI InfiniteTalk 工作流图片处理分析

## 🔍 关键发现

### 1. ImageResizeKJv2 节点 ⭐ 重要

**节点类型**: `ImageResizeKJv2`
**位置**: 图片加载后，传给 MultiTalk 节点之前

**参数配置**:
```python
参数值: [480, 832, 'lanczos', 'crop', '0, 0, 0', 'center', 2, 'cpu']

对应参数:
[0] height = 480          # 目标高度
[1] width = 832           # 目标宽度
[2] upscale_method = 'lanczos'  # 缩放方法
[3] keep_proportion = 'crop'    # 保持比例方式 ⭐ 关键！
[4] pad_color = '0, 0, 0'       # 填充颜色（黑色）
[5] crop_position = 'center'    # 裁剪位置
[6] divisible_by = 2            # 尺寸必须能被2整除
[7] device = 'cpu'              # 处理设备
```

---

## 🎯 关键参数说明

### keep_proportion = 'crop' ⭐

**这是核心功能！**

**选项**:
1. **'crop'** - 裁剪模式（工作流使用的）
   - 保持图片比例
   - 裁剪多余部分
   - 填满目标尺寸

2. **'pad'** - 填充模式
   - 保持图片比例
   - 添加黑边
   - 不裁剪

3. **'stretch'** - 拉伸模式
   - 不保持比例
   - 强制拉伸到目标尺寸
   - 可能变形

### 工作原理

#### Crop 模式（工作流使用）
```
原图: 1920x1080 (16:9)
目标: 832x480 (1.733:1)

步骤:
1. 计算缩放比例
   - 宽度比: 832/1920 = 0.433
   - 高度比: 480/1080 = 0.444
   - 使用较大的比例: 0.444

2. 缩放图片
   - 新尺寸: 1920*0.444 = 853 x 480

3. 裁剪到目标尺寸
   - 从中心裁剪: 853x480 → 832x480
   - 裁掉左右各 10.5 像素

结果: 832x480，无黑边，保持比例
```

#### Pad 模式
```
原图: 1920x1080 (16:9)
目标: 832x480 (1.733:1)

步骤:
1. 计算缩放比例
   - 使用较小的比例: 0.433

2. 缩放图片
   - 新尺寸: 832 x 468

3. 添加黑边
   - 上下各添加 6 像素黑边

结果: 832x480，有黑边，保持比例
```

---

## 📋 需要集成的参数

### 必须集成的参数

1. **keep_proportion** ⭐ 最重要
   - 选项: ['crop', 'pad', 'stretch']
   - 默认: 'crop'
   - 说明: 如何处理图片比例

2. **upscale_method**
   - 选项: ['lanczos', 'bicubic', 'bilinear', 'nearest']
   - 默认: 'lanczos'
   - 说明: 缩放算法

3. **crop_position**
   - 选项: ['center', 'top', 'bottom', 'left', 'right']
   - 默认: 'center'
   - 说明: 裁剪位置（仅 crop 模式）

4. **divisible_by**
   - 默认: 2
   - 说明: 尺寸必须能被此数整除

### 可选参数

5. **pad_color**
   - 默认: '0, 0, 0' (黑色)
   - 说明: 填充颜色（仅 pad 模式）

---

## 🎨 UI 设计建议

### 方案 A: 简化版（推荐）

```python
with gr.Accordion("📐 图片处理设置", open=True):
    keep_proportion = gr.Radio(
        choices=["crop", "pad", "stretch"],
        value="crop",
        label="图片适配方式",
        info="crop: 裁剪 | pad: 填充黑边 | stretch: 拉伸"
    )
    
    crop_position = gr.Dropdown(
        choices=["center", "top", "bottom", "left", "right"],
        value="center",
        label="裁剪位置",
        info="仅 crop 模式生效"
    )
```

### 方案 B: 完整版

```python
with gr.Accordion("📐 图片处理设置", open=True):
    with gr.Row():
        keep_proportion = gr.Radio(
            choices=["crop", "pad", "stretch"],
            value="crop",
            label="图片适配方式"
        )
        
        upscale_method = gr.Dropdown(
            choices=["lanczos", "bicubic", "bilinear", "nearest"],
            value="lanczos",
            label="缩放算法"
        )
    
    with gr.Row():
        crop_position = gr.Dropdown(
            choices=["center", "top", "bottom", "left", "right"],
            value="center",
            label="裁剪位置"
        )
        
        pad_color = gr.Textbox(
            value="0, 0, 0",
            label="填充颜色 (R,G,B)"
        )
```

---

## 🔧 代码实现

### 图片预处理函数

```python
def preprocess_image_for_infinitetalk(
    image,
    target_width,
    target_height,
    keep_proportion='crop',
    upscale_method='lanczos',
    crop_position='center',
    pad_color=(0, 0, 0),
    divisible_by=2
):
    """
    预处理图片以适配 InfiniteTalk
    
    Args:
        image: PIL Image
        target_width: 目标宽度
        target_height: 目标高度
        keep_proportion: 'crop' | 'pad' | 'stretch'
        upscale_method: 'lanczos' | 'bicubic' | 'bilinear' | 'nearest'
        crop_position: 'center' | 'top' | 'bottom' | 'left' | 'right'
        pad_color: (R, G, B) 填充颜色
        divisible_by: 尺寸必须能被此数整除
    
    Returns:
        PIL Image: 处理后的图片
    """
    from PIL import Image
    
    # 确保目标尺寸能被 divisible_by 整除
    target_width = (target_width // divisible_by) * divisible_by
    target_height = (target_height // divisible_by) * divisible_by
    
    if keep_proportion == 'stretch':
        # 直接拉伸
        return image.resize((target_width, target_height), 
                          getattr(Image, upscale_method.upper()))
    
    # 获取原始尺寸
    orig_width, orig_height = image.size
    orig_ratio = orig_width / orig_height
    target_ratio = target_width / target_height
    
    if keep_proportion == 'crop':
        # 裁剪模式：保持比例，裁掉多余部分
        if orig_ratio > target_ratio:
            # 原图更宽，按高度缩放
            new_height = target_height
            new_width = int(target_height * orig_ratio)
        else:
            # 原图更高，按宽度缩放
            new_width = target_width
            new_height = int(target_width / orig_ratio)
        
        # 缩放
        resized = image.resize((new_width, new_height),
                             getattr(Image, upscale_method.upper()))
        
        # 裁剪
        if crop_position == 'center':
            left = (new_width - target_width) // 2
            top = (new_height - target_height) // 2
        elif crop_position == 'top':
            left = (new_width - target_width) // 2
            top = 0
        elif crop_position == 'bottom':
            left = (new_width - target_width) // 2
            top = new_height - target_height
        elif crop_position == 'left':
            left = 0
            top = (new_height - target_height) // 2
        elif crop_position == 'right':
            left = new_width - target_width
            top = (new_height - target_height) // 2
        
        return resized.crop((left, top, left + target_width, top + target_height))
    
    elif keep_proportion == 'pad':
        # 填充模式：保持比例，添加黑边
        if orig_ratio > target_ratio:
            # 原图更宽，按宽度缩放
            new_width = target_width
            new_height = int(target_width / orig_ratio)
        else:
            # 原图更高，按高度缩放
            new_height = target_height
            new_width = int(target_height * orig_ratio)
        
        # 缩放
        resized = image.resize((new_width, new_height),
                             getattr(Image, upscale_method.upper()))
        
        # 创建目标尺寸的画布
        result = Image.new('RGB', (target_width, target_height), pad_color)
        
        # 居中粘贴
        left = (target_width - new_width) // 2
        top = (target_height - new_height) // 2
        result.paste(resized, (left, top))
        
        return result
```

---

## 📊 对比说明

### Crop vs Pad vs Stretch

| 模式 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **Crop** | 无黑边，画面饱满 | 可能裁掉重要内容 | 人像、特写 |
| **Pad** | 保留完整画面 | 有黑边 | 风景、全景 |
| **Stretch** | 填满画面 | 可能变形 | 不推荐 |

### 示例对比

**原图**: 1920x1080 (16:9)
**目标**: 832x480 (1.733:1)

```
Crop 模式:
┌────────────────┐
│  [  图片  ]    │  裁掉左右
│  [  完整  ]    │  无黑边
│  [  显示  ]    │
└────────────────┘

Pad 模式:
┌────────────────┐
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │  上下黑边
│  [  图片  ]    │  完整显示
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │
└────────────────┘

Stretch 模式:
┌────────────────┐
│  [  图片  ]    │  强制拉伸
│  [  变形  ]    │  可能变形
│  [  显示  ]    │
└────────────────┘
```

---

## ✅ 集成建议

### 推荐配置

**InfiniteTalk 默认设置**:
```python
keep_proportion = 'crop'      # 裁剪模式
upscale_method = 'lanczos'    # 最高质量
crop_position = 'center'      # 居中裁剪
divisible_by = 2              # 能被2整除
```

**原因**:
- ✅ 无黑边，画面更饱满
- ✅ 适合人像和特写
- ✅ 与 ComfyUI 工作流一致

---

## 🚀 下一步

1. **添加图片处理参数到 UI**
2. **实现图片预处理函数**
3. **集成到 InfiniteTalk 流程**
4. **测试不同模式效果**

**准备好集成这些参数了吗？** 🎨
