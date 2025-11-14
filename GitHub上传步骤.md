# 📤 GitHub 上传完整步骤

**创建时间**: 2025-11-14 13:59

---

## 📋 准备工作

### ✅ 已完成

1. ✅ 创建 `.gitignore` - 排除 twodog、models、outputs
2. ✅ 创建 `README.md` - 项目说明文档
3. ✅ 创建上传脚本 `UPLOAD_TO_GITHUB.bat`

### 📦 将要上传的内容

**包含**:
- ✅ `genesis/` - 核心代码
- ✅ `*.bat` - 所有启动脚本
- ✅ `*.md` - 所有文档
- ✅ `*.py` - Python 脚本
- ✅ `__init__.py`, `loader.py` 等配置文件

**排除**:
- ❌ `twodog/` - 第三方工具
- ❌ `models/` - 模型文件（太大）
- ❌ `outputs/` - 输出文件
- ❌ `python313/` - Python 环境（太大）
- ❌ `*.zip` - 压缩包
- ❌ `*.safetensors` - 模型文件

---

## 🚀 上传步骤

### 步骤 1: 在 GitHub 上创建仓库

1. 打开 GitHub: https://github.com
2. 点击右上角 `+` → `New repository`
3. 填写信息:
   - **Repository name**: `genesis_hand` 或 `wanvideo-genesis`
   - **Description**: WanVideo 视频生成平台
   - **Public** 或 **Private**: 根据需要选择
   - ⚠️ **不要**勾选 "Initialize this repository with a README"
4. 点击 `Create repository`
5. 复制仓库 URL（格式: `https://github.com/用户名/仓库名.git`）

---

### 步骤 2: 运行上传脚本

**方法 A: 使用自动脚本（推荐）**

```batch
UPLOAD_TO_GITHUB.bat
```

脚本会提示你输入:
1. GitHub 用户名
2. GitHub 邮箱
3. 提交信息（可选）
4. 仓库 URL

**方法 B: 手动命令**

```bash
# 1. 初始化 Git
git init

# 2. 配置用户信息
git config user.name "你的用户名"
git config user.email "你的邮箱"

# 3. 添加文件
git add .

# 4. 提交
git commit -m "Initial commit"

# 5. 添加远程仓库
git remote add origin https://github.com/用户名/仓库名.git

# 6. 推送
git branch -M main
git push -u origin main
```

---

### 步骤 3: 处理大文件（使用 GitHub Releases）

由于 `python313.zip` (3.6 GB) 和 `genesis.zip` (474 MB) 太大，需要通过 Releases 上传：

1. **访问仓库页面**
   ```
   https://github.com/你的用户名/仓库名
   ```

2. **创建 Release**
   - 点击右侧 `Releases` → `Create a new release`
   - Tag version: `v1.0.0`
   - Release title: `Genesis Hand v1.0.0 - 完整包`
   - Description:
     ```markdown
     # Genesis Hand v1.0.0
     
     完整的 WanVideo 视频生成平台
     
     ## 📦 包含文件
     
     - **genesis.zip** (474 MB) - 核心代码和模型
     - **python313.zip** (3.6 GB) - Python 3.13 环境（含所有依赖）
     - **int及启动文件.zip** (0.23 MB) - 初始化和启动文件
     
     ## 🚀 使用方法
     
     1. 下载所有 zip 文件
     2. 解压到同一目录
     3. 运行 `START_UI.bat`
     
     详见仓库 README.md
     ```

3. **上传文件**
   - 点击 `Attach binaries by dropping them here or selecting them`
   - 上传三个 zip 文件:
     - `genesis.zip` (474 MB) ✅
     - `int及启动文件.zip` (0.23 MB) ✅
     - ⚠️ `python313.zip` (3.6 GB) - **可能超过 2GB 限制**

4. **发布**
   - 点击 `Publish release`

---

## ⚠️ python313.zip 太大的解决方案

### 问题
`python313.zip` (3.6 GB) 超过 GitHub Release 的 2GB 单文件限制

### 解决方案

**方案 A: 分割上传**

```powershell
# 分割成 1GB 的部分
$source = "python313.zip"
$chunkSize = 1GB
$chunks = [Math]::Ceiling((Get-Item $source).Length / $chunkSize)

$stream = [System.IO.File]::OpenRead($source)
$buffer = New-Object byte[] $chunkSize

for ($i = 0; $i -lt $chunks; $i++) {
    $bytesRead = $stream.Read($buffer, 0, $chunkSize)
    $outputFile = "python313.part$($i+1).zip"
    [System.IO.File]::WriteAllBytes($outputFile, $buffer[0..($bytesRead-1)])
    Write-Host "Created $outputFile"
}
$stream.Close()
```

然后在 Release 中上传所有分割文件，并在说明中添加合并命令:

```batch
REM Windows 合并命令
copy /b python313.part1.zip+python313.part2.zip+python313.part3.zip+python313.part4.zip python313.zip
```

**方案 B: 使用外部存储**

将 `python313.zip` 上传到:
- 百度网盘
- 阿里云盘
- OneDrive
- Google Drive

然后在 Release 说明中添加下载链接

**方案 C: 不包含 Python 环境**

在 README 中说明用户需要自己安装 Python 3.13 和依赖

---

## 📝 上传后的 README 更新

上传完成后，在 README.md 中添加下载链接:

```markdown
## 📥 下载

### 完整包（推荐）

从 [Releases](https://github.com/你的用户名/仓库名/releases) 下载:

1. **genesis.zip** (474 MB) - 核心代码
2. **python313.zip** (3.6 GB) - Python 环境
3. **int及启动文件.zip** (0.23 MB) - 启动文件

### 仅代码

```bash
git clone https://github.com/你的用户名/仓库名.git
```

然后自行配置 Python 环境和下载模型
```

---

## ✅ 检查清单

上传前检查:

- [ ] `.gitignore` 已创建
- [ ] `README.md` 已创建
- [ ] 已排除 `twodog/`
- [ ] 已排除 `models/`
- [ ] 已排除 `python313/`
- [ ] 已排除 `*.zip`

上传后检查:

- [ ] 仓库已创建
- [ ] 代码已推送
- [ ] Release 已创建
- [ ] 小文件已上传到 Release
- [ ] 大文件处理方案已确定
- [ ] README 中包含下载说明

---

## 🎯 推荐流程

1. ✅ 运行 `UPLOAD_TO_GITHUB.bat`
2. ✅ 等待代码推送完成
3. ✅ 在 GitHub 上创建 Release
4. ✅ 上传 `genesis.zip` 和 `int及启动文件.zip`
5. ⚠️ 处理 `python313.zip`:
   - 选项 A: 分割上传
   - 选项 B: 使用网盘
   - 选项 C: 不包含
6. ✅ 更新 Release 说明
7. ✅ 测试下载和使用

---

**准备好了吗？运行 `UPLOAD_TO_GITHUB.bat` 开始上传！** 🚀
