@echo off
echo ========================================
echo   Genesis WanVideo Diagnostics
echo ========================================
echo.

cd /d "%~dp0"

echo [1] Checking Python...
python313\python.exe --version
echo.

echo [2] Checking model directories...
echo diffusion_models:
if exist "genesis\models\diffusion_models" (
    echo   EXISTS
    dir "genesis\models\diffusion_models\wan" 2>nul | find "wan2.2" | find /c ".safetensors"
) else (
    echo   MISSING!
)
echo.

echo vae:
if exist "genesis\models\vae" (
    echo   EXISTS
    dir "genesis\models\vae" | find /c ".safetensors"
) else (
    echo   MISSING!
)
echo.

echo text_encoders:
if exist "genesis\models\text_encoders" (
    echo   EXISTS
    dir "genesis\models\text_encoders" | find /c ".safetensors"
) else (
    echo   MISSING!
)
echo.

echo [3] Testing node loading...
python313\python.exe -c "import sys; sys.path.insert(0, '.'); from genesis.apps.wanvideo_gradio_app import NODE_CLASS_MAPPINGS; print(f'Loaded {len(NODE_CLASS_MAPPINGS)} nodes')"
echo.

echo [4] Checking CUDA...
python313\python.exe -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
echo.

echo [5] Checking memory...
python313\python.exe -c "import torch; print(f'GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB') if torch.cuda.is_available() else print('No CUDA')"
echo.

echo ========================================
echo   Diagnostics Complete
echo ========================================
echo.
echo Please copy the output above and send to support.
echo.
pause
