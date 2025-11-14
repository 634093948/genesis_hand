# 🎵 MelBandRoformer 模型设置说明

**问题**: 生成时提示 "Invalid WanVideo model selected"，尝试加载 `MelBandRoformer_fp32.safetensors`
**原因**: MelBandRoformer 模型未正确链接到项目模型目录

---

## 🔍 问题分析

### 错误信息

```
[DEBUG] Loading model: MelBandRoformer_fp32.safetensors
ValueError: Invalid WanVideo model selected
```

### 原因

MelBandRoformer 是音频处理模型，应该在 `models/audio_encoders/` 目录中，但可能：
1. 模型文件不存在
2. 模型文件在 ComfyUI 目录中，但未链接到当前项目

---

## ✅ 解决方案

### 方案 1: 自动设置（推荐）

**运行设置脚本**:
```bash
SETUP_MELBAND_MODEL.bat
```

**脚本功能**:
1. 自动搜索 MelBandRoformer 模型文件
2. 在以下位置搜索:
   - `e:\liliyuanshangmie\ComfyUI\models`
   - `e:\liliyuanshangmie\twodog\ComfyUI\models`
   - `%USERPROFILE%\ComfyUI\models`
3. 自动创建符号链接到 `models/audio_encoders/`
4. 验证设置

**注意**: 需要以**管理员身份**运行

---

### 方案 2: 手动设置

#### 步骤 1: 查找模型文件

在 ComfyUI 目录中查找 `MelBandRoformer_fp32.safetensors`:

```powershell
# 在 PowerShell 中运行
Get-ChildItem -Path "e:\liliyuanshangmie" -Filter "MelBandRoformer*.safetensors" -Recurse
```

可能的位置:
- `e:\liliyuanshangmie\ComfyUI\models\audio_encoders\`
- `e:\liliyuanshangmie\twodog\ComfyUI\models\audio_encoders\`

#### 步骤 2: 创建目录

```powershell
# 创建 audio_encoders 目录
New-Item -ItemType Directory -Path "e:\liliyuanshangmie\genesis_hand\models\audio_encoders" -Force
```

#### 步骤 3: 创建符号链接

**以管理员身份运行 PowerShell**:

```powershell
# 替换 <源路径> 为实际找到的模型文件路径
mklink "e:\liliyuanshangmie\genesis_hand\models\audio_encoders\MelBandRoformer_fp32.safetensors" "<源路径>\MelBandRoformer_fp32.safetensors"
```

**示例**:
```powershell
mklink "e:\liliyuanshangmie\genesis_hand\models\audio_encoders\MelBandRoformer_fp32.safetensors" "e:\liliyuanshangmie\ComfyUI\models\audio_encoders\MelBandRoformer_fp32.safetensors"
```

---

### 方案 3: 复制文件

如果不想使用符号链接，可以直接复制文件:

```powershell
# 复制文件
Copy-Item "<源路径>\MelBandRoformer_fp32.safetensors" "e:\liliyuanshangmie\genesis_hand\models\audio_encoders\MelBandRoformer_fp32.safetensors"
```

**注意**: 这会占用额外的磁盘空间（模型文件较大）

---

## 🔍 验证设置

### 检查文件是否存在

```powershell
Test-Path "e:\liliyuanshangmie\genesis_hand\models\audio_encoders\MelBandRoformer_fp32.safetensors"
```

应该返回 `True`

### 查看文件信息

```powershell
Get-Item "e:\liliyuanshangmie\genesis_hand\models\audio_encoders\MelBandRoformer_fp32.safetensors"
```

如果是符号链接，会显示 `LinkType: SymbolicLink`

---

## 📁 最终目录结构

```
genesis_hand/
└── models/
    ├── audio_encoders/
    │   └── MelBandRoformer_fp32.safetensors  ← 符号链接或实际文件
    ├── vae/
    ├── text_encoders/
    ├── wanvideo/
    └── wav2vec2/
```

---

## ⚠️ 常见问题

### Q1: 找不到 MelBandRoformer 模型文件

**A**: 可能需要下载模型文件

**下载位置**:
- 从 ComfyUI 的模型管理器下载
- 或从 Hugging Face 下载

**放置位置**:
- `models/audio_encoders/MelBandRoformer_fp32.safetensors`

---

### Q2: mklink 命令失败

**错误**: "你没有足够的权限执行此操作"

**解决**:
1. 以管理员身份运行 PowerShell 或 CMD
2. 右键点击 `SETUP_MELBAND_MODEL.bat` → "以管理员身份运行"

---

### Q3: 符号链接 vs 复制文件

**符号链接**:
- ✅ 不占用额外空间
- ✅ 自动同步更新
- ❌ 需要管理员权限

**复制文件**:
- ✅ 不需要管理员权限
- ❌ 占用额外空间（~200MB）
- ❌ 需要手动更新

**推荐**: 使用符号链接

---

### Q4: 如何删除符号链接

```powershell
# 删除符号链接（不会删除源文件）
Remove-Item "e:\liliyuanshangmie\genesis_hand\models\audio_encoders\MelBandRoformer_fp32.safetensors"
```

---

## 🎯 MelBandRoformer 模型说明

### 用途

MelBandRoformer 是一个音频处理模型，用于:
- 音频分离
- 音频增强
- 音频特征提取

### 在 WanVideo 中的作用

可能用于:
- InfiniteTalk 的音频处理
- 音频质量增强
- 音频特征提取

---

## 📝 设置步骤总结

### 快速设置（推荐）

1. **以管理员身份运行**:
   ```bash
   SETUP_MELBAND_MODEL.bat
   ```

2. **等待脚本完成**

3. **验证设置**

4. **重新启动应用**:
   ```bash
   START_UI.bat
   ```

---

### 手动设置

1. **查找模型文件**
2. **创建 audio_encoders 目录**
3. **创建符号链接或复制文件**
4. **验证文件存在**
5. **重新启动应用**

---

## ✅ 设置完成后

### 验证

1. 启动应用
2. 尝试生成视频
3. 检查日志，不应该再有 "Invalid WanVideo model selected" 错误

### 预期日志

```
[DEBUG] Loading model: MelBandRoformer_fp32.safetensors
[INFO] MelBandRoformer model loaded successfully
```

---

**🎉 设置完成后，应该就能正常生成了！** 🚀
