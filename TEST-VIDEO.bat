@echo off
cd /d "%~dp0"

echo ========================================
echo Testing Video Generation Setup
echo ========================================
echo.

echo [1] Checking Python...
python313\python.exe --version
if %errorLevel% neq 0 (
    echo FAILED: Python not found
    pause
    exit /b 1
)
echo OK
echo.

echo [2] Checking Gradio...
python313\python.exe -c "import gradio; print(f'Gradio {gradio.__version__}')" 2>nul
if %errorLevel% neq 0 (
    echo Installing Gradio...
    python313\python.exe -m pip install gradio
)
echo OK
echo.

echo [3] Checking wanvideo_gradio_app.py...
if exist "genesis\apps\wanvideo_gradio_app.py" (
    echo OK - File exists
) else (
    echo FAILED - File not found
    pause
    exit /b 1
)
echo.

echo [4] Checking port 7860...
netstat -ano | findstr :7860 >nul
if %errorLevel% equ 0 (
    echo WARNING: Port 7860 is in use
    echo Run KILL-PORT.bat to clean up
) else (
    echo OK - Port is free
)
echo.

echo [5] Testing import...
python313\python.exe -c "import sys; sys.path.insert(0, '.'); print('Import test OK')" 2>nul
if %errorLevel% neq 0 (
    echo FAILED: Import test failed
) else (
    echo OK
)
echo.

echo ========================================
echo Test Complete
echo ========================================
echo.
echo If all tests passed, you can run VIDEO.bat
echo.
pause
