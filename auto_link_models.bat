@echo off
chcp 65001 >nul
echo ======================================================================
echo 自动链接 ComfyUI 模型到 Genesis Hand
echo ======================================================================
echo.

set "SOURCE_DIR=E:\liliyuanshangmie\Fuxkcomfy_lris_kernel_gen2-4_speed_safe\FuxkComfy\models"
set "TARGET_DIR=%~dp0models"

echo 源目录: %SOURCE_DIR%
echo 目标目录: %TARGET_DIR%
echo.

REM 创建目标目录
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

echo 1. 链接 WanVideo 模型目录...
if exist "%SOURCE_DIR%\diffusion_models\wan" (
    if exist "%TARGET_DIR%\wanvideo" (
        echo    删除旧链接...
        rmdir "%TARGET_DIR%\wanvideo" 2>nul
    )
    mklink /J "%TARGET_DIR%\wanvideo" "%SOURCE_DIR%\diffusion_models\wan"
    if %ERRORLEVEL% EQU 0 (
        echo    ✅ wanvideo 链接成功
    ) else (
        echo    ❌ wanvideo 链接失败 ^(可能需要管理员权限^)
    )
) else (
    echo    ⚠️  源目录不存在
)
echo.

echo 2. 链接 VAE 模型目录...
if exist "%SOURCE_DIR%\vae" (
    if exist "%TARGET_DIR%\vae" (
        echo    删除旧链接...
        rmdir "%TARGET_DIR%\vae" 2>nul
    )
    mklink /J "%TARGET_DIR%\vae" "%SOURCE_DIR%\vae"
    if %ERRORLEVEL% EQU 0 (
        echo    ✅ vae 链接成功
    ) else (
        echo    ❌ vae 链接失败
    )
) else (
    echo    ⚠️  源目录不存在
)
echo.

echo 3. 链接 CLIP Vision 模型目录...
if exist "%SOURCE_DIR%\clip_vision" (
    if exist "%TARGET_DIR%\clip_vision" (
        echo    删除旧链接...
        rmdir "%TARGET_DIR%\clip_vision" 2>nul
    )
    mklink /J "%TARGET_DIR%\clip_vision" "%SOURCE_DIR%\clip_vision"
    if %ERRORLEVEL% EQU 0 (
        echo    ✅ clip_vision 链接成功
    ) else (
        echo    ❌ clip_vision 链接失败
    )
) else (
    echo    ⚠️  源目录不存在
)
echo.

echo 4. 链接 Text Encoders 目录...
if exist "%SOURCE_DIR%\clip" (
    if exist "%TARGET_DIR%\text_encoders" (
        echo    删除旧链接...
        rmdir "%TARGET_DIR%\text_encoders" 2>nul
    )
    mklink /J "%TARGET_DIR%\text_encoders" "%SOURCE_DIR%\clip"
    if %ERRORLEVEL% EQU 0 (
        echo    ✅ text_encoders 链接成功
    ) else (
        echo    ❌ text_encoders 链接失败
    )
) else (
    echo    ⚠️  源目录不存在
)
echo.

echo 5. 检查 Wav2Vec 模型...
REM Wav2Vec 模型可能不在 ComfyUI 中，需要单独下载
if not exist "%TARGET_DIR%\wav2vec2" (
    mkdir "%TARGET_DIR%\wav2vec2"
    echo    ⚠️  wav2vec2 目录已创建，但需要手动下载模型
    echo       参考: models\wav2vec2\README.md
) else (
    echo    ✅ wav2vec2 目录已存在
)
echo.

echo ======================================================================
echo 链接完成！
echo ======================================================================
echo.
echo 下一步:
echo   1. 运行: python check_infinitetalk_deps.py
echo   2. 检查模型是否正确链接
echo   3. 启动 UI 测试
echo.
echo 注意:
echo   - 链接的目录不占用额外空间
echo   - 修改链接中的文件会影响原始 ComfyUI 模型
echo   - 删除链接使用: rmdir models\^<目录名^>
echo.
pause
