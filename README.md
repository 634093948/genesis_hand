# Genesis Hand - WanVideo 视频生成平台

基于 WanVideo 的统一视频生成平台，支持文生视频、图生视频等多种模式。

---

## 🎯 主要功能

### 视频生成模式

1. **文生视频 (Text to Video)**
   - 从文本描述生成视频
   - 支持多种模型和 VAE

2. **图生视频 - InfiniteTalk**
   - 音频驱动的人物说话视频
   - 支持无音频模式（静默）
   - 模型缓存机制，性能提升 40-45%

3. **图生视频 - WanAnimate**
   - 姿态/面部驱动的动画
   - 支持自定义控制

4. **图生视频 - Standard I2V**
   - 标准图片到视频转换

---

## 🚀 快速开始

### 环境要求

- **Python**: 3.13（项目自带 python313）
- **CUDA**: 支持 CUDA 的 NVIDIA 显卡
- **VRAM**: 建议 12GB+

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone <your-repo-url>
   cd genesis_hand
   ```

2. **准备模型文件**
   
   需要手动下载模型文件到 `models/` 目录：
   
   ```
   models/
   ├── diffusion_models/    # Diffusion 模型
   ├── vae/                 # VAE 模型
   ├── text_encoders/       # T5 文本编码器
   ├── audio_encoders/      # 音频编码器
   └── wav2vec2/           # Wav2Vec 模型
   ```

3. **启动 UI**
   ```batch
   START_UI.bat          # 快速启动
   WANVIDEO_UI.bat       # 完整启动
   RUN.bat               # 菜单启动
   ```

---

## 📦 项目结构

```
genesis_hand/
├── genesis/              # 核心代码
│   ├── apps/            # 应用程序
│   │   └── wanvideo_gradio_app.py  # 主 UI
│   ├── compat/          # ComfyUI 兼容层
│   └── examples/        # 示例代码
├── python313/           # Python 3.13 环境（需单独下载）
├── models/              # 模型文件（需单独下载）
├── outputs/             # 输出文件
├── *.bat               # 启动脚本
└── README.md           # 本文件
```

---

## 🎨 功能特性

### UI 优化

- ✅ 统一视频生成界面
- ✅ 智能动态 UI（根据模式自动调整）
- ✅ 模型配置折叠面板
- ✅ 性能优化折叠面板
- ✅ LoRA 支持

### 性能优化

- ✅ **模型缓存机制** - 性能提升 40-45%
- ✅ **Torch Compile** - 编译加速
- ✅ **智能 VRAM 管理** - 自动优化内存
- ✅ **块交换** - 减少 VRAM 占用

### 量化支持

- FP8 量化（fp8_e4m3fn, fp8_e5m2）
- FP4 量化（fp4_experimental, fp4_scaled）
- NF4/INT8 量化

### 注意力模式

- sdpa - 标准注意力
- flash_attn - Flash Attention
- sageattn - Sage Attention
- sageattn_3_fp4 - FP4 注意力（RTX 5090）
- sageattn_3_fp8 - FP8 注意力（最快）

---

## 📊 性能对比

### InfiniteTalk 模型缓存效果

| 场景 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| **第一次生成** | 35-56 秒 | 35-56 秒 | 0% |
| **第二次生成** | 35-56 秒 | **21-31 秒** | **40-45%** ✅ |
| **后续生成** | 35-56 秒 | **21-31 秒** | **40-45%** ✅ |

**节省时间**: 每次生成节省 **14-25 秒**！

---

## 🔧 配置说明

### 模型配置

在 UI 中可以选择：
- **Diffusion Model**: 主生成模型
- **VAE Model**: 视频编码器
- **T5 Text Encoder**: 文本编码器

### 优化参数

- **Torch Compile**: 启用编译加速
- **Block Swap**: 块交换数量（建议 20-40）
- **VRAM Threshold**: VRAM 阈值（建议 50%）
- **Quantization**: 量化模式
- **Attention Mode**: 注意力模式

---

## 📝 启动脚本说明

| 脚本 | 功能 | 推荐场景 |
|------|------|----------|
| **START_UI.bat** | 快速启动 UI | 日常使用 |
| **WANVIDEO_UI.bat** | 完整启动（带说明） | 首次使用 |
| **RUN.bat** | 菜单式启动 | 多功能切换 |
| **QUICK-TEST.bat** | 快速测试 | 测试环境 |
| **DIAGNOSE.bat** | 环境诊断 | 问题排查 |

---

## 🐛 常见问题

### 1. 模型未找到

**解决**: 确保模型文件已下载到 `models/` 目录

### 2. VRAM 不足

**解决**: 
- 增加块交换数量
- 启用智能 VRAM 管理
- 降低分辨率或帧数

### 3. 端口被占用

**解决**: 运行 `CLEAN_PORT.bat` 清理端口

---

## 📚 文档

- `INFINITETALK_DEPS_COMPLETE.md` - InfiniteTalk 完整优化报告
- `模型缓存机制实施完成.md` - 缓存机制详细说明
- `Python环境说明.md` - Python 环境配置
- `所有启动脚本检查报告.md` - 启动脚本说明

---

## 🔄 更新日志

### v3.0 (2025-11-14)

**主要更新**:
- ✅ UI 重构 - 统一视频生成界面
- ✅ 模型缓存机制 - 性能提升 40-45%
- ✅ 完整量化支持 - 12 个量化选项
- ✅ 完整注意力模式 - 8 个注意力模式
- ✅ InfiniteTalk 优化参数支持
- ✅ MelBandRoformer 音频模型设置

**修复**:
- ✅ 模型选择 "Invalid model" 错误
- ✅ 优化参数传递问题
- ✅ 依赖缺失问题

---

## 📄 许可证

本项目基于 WanVideo 和 ComfyUI 开发。

---

## 🙏 致谢

- [WanVideo](https://github.com/WanVideo) - 视频生成模型
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) - UI 框架
- [Gradio](https://gradio.app/) - Web UI 库

---

## 📧 联系方式

如有问题或建议，欢迎提交 Issue。

---

**注意**: 
1. 本仓库不包含模型文件和 Python 环境，需要单独下载
2. 模型文件较大，建议使用高速网络下载
3. Python 环境已配置完整依赖，建议使用项目自带的 python313
