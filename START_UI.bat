@echo off
chcp 65001 >nul
cd /d "%~dp0"
title WanVideo Genesis UI
color 0A

echo.
echo ========================================
echo   WanVideo Genesis - Starting...
echo ========================================
echo.

REM Kill all Python processes using port 7860
echo Cleaning port 7860...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :7860') do (
    echo Killing process %%a
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul

echo Starting UI...
echo Browser will open: http://localhost:7860
echo.

python313\python.exe genesis\apps\wanvideo_gradio_app.py

pause
