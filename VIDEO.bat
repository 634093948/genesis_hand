@echo off
cd /d "%~dp0"
title Genesis - Video Generation

echo.
echo ========================================
echo   WanVideo - Text to Video Generation
echo ========================================
echo.

echo [1/4] Checking port 7860...
netstat -ano | findstr :7860 >nul
if %errorLevel% equ 0 (
    echo Port 7860 is in use, cleaning up...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :7860') do taskkill /F /PID %%a 2>nul
    timeout /t 2 /nobreak >nul
) else (
    echo Port 7860 is free
)

echo.
echo [2/4] Checking dependencies...
python313\python.exe -m pip install --quiet gradio torch numpy 2>nul

echo.
echo [3/4] Starting WanVideo UI...
echo This will open at http://localhost:7860
echo.
echo Features:
echo - Model selection (Diffusion Models)
echo - VAE selection
echo - T5 Text Encoder selection
echo - LoRA support
echo - Video parameters (width, height, frames, fps)
echo - Advanced optimizations
echo.

echo [4/4] Launching...
python313\python.exe genesis\apps\wanvideo_gradio_app.py

pause
