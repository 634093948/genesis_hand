@echo off
echo ================================
echo   Fixing Model Directory Links
echo ================================
echo.
echo This will create missing symbolic links:
echo   - genesis\models\diffusion_models
echo   - genesis\models\unet
echo.
echo Administrator privileges required!
echo.
pause

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0FIX-MODELS.ps1"
