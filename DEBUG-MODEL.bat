@echo off
echo ========================================
echo   Debug Model Loading
echo ========================================
echo.

cd /d "%~dp0"

echo Testing model file access...
python313\python.exe -c "import sys; sys.path.insert(0, '.'); from safetensors import safe_open; path = r'E:\liliyuanshangmie\Fuxkcomfy_lris_kernel_gen2-4_speed_safe\FuxkComfy\models\diffusion_models\wan\maga\wan2.2-rapid-mega-aio-nsfw-v9.safetensors'; f = safe_open(path, framework='pt'); keys = list(f.keys())[:10]; print(f'Model keys (first 10): {keys}'); print(f'Total keys: {len(list(f.keys()))}')"

echo.
pause
