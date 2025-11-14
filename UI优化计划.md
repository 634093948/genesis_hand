# 🎨 UI 优化计划

## 优化目标

### 1. InfiniteTalk 宽高比保持
- ✅ 添加宽高比锁定功能
- ✅ 自动计算另一维度
- ✅ 参考 ComfyUI 工作流节点

### 2. 参数分类优化
- ✅ 共通参数（所有模式）
  - 模型选择（Diffusion, VAE, T5）
  - 量化设置
  - 精度设置
  - 注意力模式
  - VRAM 管理
- ✅ 模式特定参数
  - InfiniteTalk 专属
  - WanAnimate 专属
  - Standard I2V 专属

### 3. 代码模块化
- ✅ UI 组件封装
- ✅ 参数处理函数
- ✅ 便于后续添加功能

---

## 实施步骤

### Step 1: 添加宽高比保持功能

```python
# 宽高比计算函数
def calculate_aspect_ratio_dimensions(width, height, lock_aspect, changed_dimension):
    """
    根据锁定的宽高比计算另一维度
    
    Args:
        width: 当前宽度
        height: 当前高度
        lock_aspect: 是否锁定宽高比
        changed_dimension: 'width' 或 'height'，表示哪个维度被改变
    
    Returns:
        (new_width, new_height)
    """
    if not lock_aspect:
        return width, height
    
    # 计算宽高比
    aspect_ratio = width / height
    
    if changed_dimension == 'width':
        # 宽度改变，调整高度
        new_height = round(width / aspect_ratio / 16) * 16  # 保持16的倍数
        return width, new_height
    else:
        # 高度改变，调整宽度
        new_width = round(height * aspect_ratio / 16) * 16
        return new_width, height
```

### Step 2: UI 重新组织

```
图生视频 (Image to Video)
├── 输入区域
│   ├── 模式选择 (InfiniteTalk / WanAnimate / Standard)
│   ├── 输入图片
│   └── 提示词 (Positive / Negative)
│
├── 共通参数 (所有模式)
│   ├── 📐 视频尺寸
│   │   ├── 宽度 / 高度
│   │   ├── 🔒 锁定宽高比
│   │   └── 帧数 / FPS
│   │
│   ├── 🎨 生成参数
│   │   ├── Steps / CFG / Shift
│   │   ├── Seed
│   │   └── Scheduler
│   │
│   ├── 🧠 模型选择
│   │   ├── Diffusion Model
│   │   ├── VAE Model
│   │   └── T5 Encoder
│   │
│   └── ⚙️ 高级设置 (折叠)
│       ├── 精度 (Base Precision)
│       ├── 量化 (Quantization)
│       ├── 注意力模式 (Attention)
│       └── VRAM 管理
│
└── 模式特定参数 (动态显示)
    ├── 🎙️ InfiniteTalk 设置
    │   ├── 音频文件
    │   ├── Frame Window Size
    │   ├── Motion Frame
    │   └── Wav2Vec 设置 (折叠)
    │
    ├── 🎭 WanAnimate 设置
    │   ├── 姿态图片
    │   ├── 面部图片
    │   ├── Pose/Face Strength
    │   └── Color Match
    │
    └── 📹 Standard I2V 设置
        └── (基础参数即可)
```

### Step 3: 代码模块化

```python
class UIComponents:
    """UI 组件管理类"""
    
    @staticmethod
    def create_common_params():
        """创建共通参数组件"""
        pass
    
    @staticmethod
    def create_infinitetalk_params():
        """创建 InfiniteTalk 参数组件"""
        pass
    
    @staticmethod
    def create_wananimate_params():
        """创建 WanAnimate 参数组件"""
        pass

class ParameterManager:
    """参数管理类"""
    
    @staticmethod
    def validate_params(mode, **kwargs):
        """验证参数"""
        pass
    
    @staticmethod
    def get_default_params(mode):
        """获取默认参数"""
        pass
```

---

## 详细功能

### 宽高比保持

```python
# UI 组件
with gr.Row():
    i2v_width = gr.Slider(64, 2048, value=832, step=16, label="宽度 (Width)")
    i2v_height = gr.Slider(64, 2048, value=480, step=16, label="高度 (Height)")
    lock_aspect_ratio = gr.Checkbox(value=True, label="🔒 锁定宽高比")

# 事件处理
def on_width_change(width, height, lock):
    if lock:
        aspect = 832 / 480  # 初始宽高比
        new_height = round(width / aspect / 16) * 16
        return gr.update(value=new_height)
    return gr.update()

def on_height_change(width, height, lock):
    if lock:
        aspect = 832 / 480
        new_width = round(height * aspect / 16) * 16
        return gr.update(value=new_width)
    return gr.update()

i2v_width.change(on_width_change, [i2v_width, i2v_height, lock_aspect_ratio], [i2v_height])
i2v_height.change(on_height_change, [i2v_width, i2v_height, lock_aspect_ratio], [i2v_width])
```

---

## 实施优先级

1. **高优先级** (立即实施)
   - ✅ 宽高比保持功能
   - ✅ 参数分类重组

2. **中优先级** (后续实施)
   - ⚠️ 代码模块化
   - ⚠️ 参数验证

3. **低优先级** (可选)
   - 📝 参数预设
   - 📝 参数导入/导出

---

## 兼容性保证

- ✅ 不影响现有功能
- ✅ 保持所有参数传递
- ✅ 向后兼容
- ✅ 渐进式优化

---

## 测试清单

- [ ] InfiniteTalk 模式正常生成
- [ ] WanAnimate 模式正常生成
- [ ] Standard I2V 模式正常生成
- [ ] 宽高比锁定功能正常
- [ ] 参数切换无错误
- [ ] 所有高级参数生效
