@echo off
echo ========================================
echo   Complete System Test
echo ========================================
echo.

cd /d "%~dp0"

echo [1] Testing imports...
python313\python.exe -c "import sys; sys.path.insert(0, '.'); from genesis.apps import wanvideo_gradio_app; print('OK')"
if %errorLevel% neq 0 (
    echo FAILED
    pause
    exit /b 1
)

echo [2] Testing BaseModel...
python313\python.exe -c "from genesis.compat import comfy_stub; from comfy.model_base import BaseModel; m = BaseModel(); print(f'latent_format: {m.latent_format}'); print('OK')"
if %errorLevel% neq 0 (
    echo FAILED
    pause
    exit /b 1
)

echo [3] Testing ModelPatcher...
python313\python.exe -c "from genesis.compat import comfy_stub; from comfy.model_patcher import ModelPatcher; from comfy.model_base import BaseModel; m = BaseModel(); p = ModelPatcher(m); print(f'patcher.latent_format: {p.latent_format}'); print('OK')"
if %errorLevel% neq 0 (
    echo FAILED
    pause
    exit /b 1
)

echo [4] Testing PromptServer...
python313\python.exe -c "from genesis.compat import comfy_stub; from server import PromptServer; ps = PromptServer(); print('OK')"
if %errorLevel% neq 0 (
    echo FAILED
    pause
    exit /b 1
)

echo [5] Testing TAESD...
python313\python.exe -c "from genesis.compat import comfy_stub; from comfy.taesd.taesd import TAESD; t = TAESD(); print('OK')"
if %errorLevel% neq 0 (
    echo FAILED
    pause
    exit /b 1
)

echo.
echo ========================================
echo   All Tests Passed!
echo ========================================
echo.
echo You can now run VIDEO.bat to generate videos.
echo.
pause
