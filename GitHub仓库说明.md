# GitHub 仓库说明

## 仓库信息
- **仓库地址**: https://github.com/634093948/genesis_hand
- **分支**: main
- **提交ID**: 61cb02e7

## 已上传内容
本仓库包含 Genesis Hand - WanVideo 视频生成平台的核心代码和配置文件，共 **284 个文件**。

### 主要内容
- **genesis/** - 核心代码目录
  - 核心引擎和节点系统
  - Gradio UI 应用
  - API 服务器
  - 工具和辅助脚本
  
- **配置和脚本文件**
  - 各种批处理启动脚本 (.bat)
  - PowerShell 脚本 (.ps1)
  - Python 工具脚本
  
- **文档**
  - README.md - 项目说明
  - 各种功能说明和修复文档

## 已排除内容（不在仓库中）

以下内容已通过 `.gitignore` 排除，**不会上传到 GitHub**：

### 1. 文件夹
- **models/** - 模型文件夹（用户需自行下载模型）
- **twodog/** - 私有文件夹
- **python313/** - Python 环境（用户需自行安装 Python）
- **outputs/** - 输出文件夹（运行时生成）

### 2. 压缩包
- **genesis.zip** - Genesis 源码压缩包
- **int及启动文件.zip** - 启动文件压缩包
- **python313.zip** - Python 环境压缩包

### 3. 其他
- **__pycache__/** - Python 缓存
- **\*.pyc** - Python 编译文件

## 使用说明

### 克隆仓库
```bash
git clone https://github.com/634093948/genesis_hand.git
cd genesis_hand
```

### 环境准备
1. **安装 Python 3.13**
   - 下载并安装 Python 3.13
   - 或使用本地的 `python313/` 文件夹（如果有）

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **下载模型**
   - 参考 `模型下载指南.md`
   - 将模型放置到 `models/` 文件夹

4. **创建输出文件夹**
   ```bash
   mkdir outputs
   ```

### 运行项目
```bash
# 启动 UI
RUN.bat

# 或使用 Python 直接运行
python genesis/apps/wanvideo_gradio_app.py
```

## 注意事项
- 本仓库不包含模型文件，需要自行下载
- 本仓库不包含 Python 环境，需要自行安装
- 首次运行前请确保已完成环境准备

## 更新日志
- 2024-11-14: 初始提交，包含完整的项目代码
