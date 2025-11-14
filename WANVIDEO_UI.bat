@echo off
chcp 65001 >nul
cd /d "%~dp0"
title WanVideo Genesis - Unified Video Generation UI
color 0A

echo.
echo ============================================================
echo   WanVideo Genesis - Unified Video Generation Platform
echo ============================================================
echo.

echo [1/4] Cleaning port 7860...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :7860') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul
echo Port cleaned

echo.
echo [2/4] Checking dependencies...
python313\python.exe -m pip install --quiet gradio torch numpy pillow 2>nul
echo Dependencies OK

echo.
echo [3/4] Starting WanVideo Genesis UI...
echo This will open at http://localhost:7860
echo.
echo ============================================================
echo   New Features in v3.0:
echo ============================================================
echo.
echo   - Unified Video Generation (Text/Image to Video)
echo   - InfiniteTalk (Audio-driven)
echo   - WanAnimate (Pose/Face-driven)
echo   - Standard I2V
echo   - Smart Dynamic UI
echo   - Image Processing Parameters
echo   - Image Generation (Coming Soon)
echo.
echo ============================================================

echo.
echo [4/4] Launching...
echo.
python313\python.exe genesis\apps\wanvideo_gradio_app.py

echo.
echo ============================================================
echo   Application closed
echo ============================================================
pause
