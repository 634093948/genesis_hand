@echo off
cd /d "%~dp0"
title Genesis AI Launcher

:MENU
cls
echo.
echo ========================================
echo   Genesis AI - Select Mode
echo ========================================
echo.
echo   1. Video Generation (WanVideo)
echo   2. Image Generation (Basic)
echo   3. Check Environment
echo   4. Exit
echo.
echo ========================================
echo.

choice /C 1234 /N /M "Please select (1-4): "

if errorlevel 4 goto EXIT
if errorlevel 3 goto CHECK
if errorlevel 2 goto IMAGE
if errorlevel 1 goto VIDEO

:VIDEO
cls
echo.
echo ========================================
echo   Starting Video Generation Mode
echo ========================================
echo.

echo [1/3] Checking port 7860...
netstat -ano | findstr :7860 >nul
if %errorLevel% equ 0 (
    echo Port in use, cleaning up...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :7860') do taskkill /F /PID %%a 2>nul
    timeout /t 2 /nobreak >nul
)

echo [2/3] Installing dependencies...
python313\python.exe -m pip install --quiet gradio torch numpy 2>nul

echo [3/3] Starting WanVideo UI...
echo This will open at http://localhost:7860
echo.

python313\python.exe genesis\apps\wanvideo_gradio_app.py

pause
goto MENU

:IMAGE
cls
echo.
echo ========================================
echo   Starting Image Generation Mode
echo ========================================
echo.
echo Installing dependencies...
python313\python.exe -m pip install --quiet flask flask-cors flask-socketio gradio 2>nul

echo Starting backend server...
start /MIN "Genesis-Backend" python313\python.exe genesis\examples\start_advanced_server.py

echo Waiting for server...
timeout /t 10 /nobreak >nul

echo Starting Gradio UI...
echo.

python313\python.exe genesis\examples\gradio_ui.py

taskkill /F /FI "WINDOWTITLE eq Genesis-Backend*" >nul 2>&1
pause
goto MENU

:CHECK
cls
call CHECK.bat
goto MENU

:EXIT
echo.
echo Goodbye!
timeout /t 2 /nobreak >nul
exit
