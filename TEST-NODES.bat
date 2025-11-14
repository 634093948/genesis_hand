@echo off
echo Testing WanVideo nodes loading...
echo.

cd /d "%~dp0"

python313\python.exe -c "import sys; sys.path.insert(0, '.'); from genesis.apps.wanvideo_gradio_app import NODE_CLASS_MAPPINGS; print(f'Loaded {len(NODE_CLASS_MAPPINGS)} nodes'); print('Essential nodes:'); essential = ['WanVideoModelLoader', 'WanVideoVAELoader', 'WanVideoSampler', 'WanVideoDecode']; [print(f'  {n}: {\"OK\" if n in NODE_CLASS_MAPPINGS else \"MISSING\"}') for n in essential]"

echo.
pause
