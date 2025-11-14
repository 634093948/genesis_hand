@echo off
echo ========================================
echo   Test Scheduler Support
echo ========================================
echo.

cd /d "%~dp0"

echo Testing scheduler availability...
python313\python.exe -c "from genesis.custom_nodes.Comfyui.ComfyUI-WanVideoWrapper.wanvideo.schedulers import scheduler_list; print(f'Available schedulers: {len(scheduler_list)}'); [print(f'  - {s}') for s in scheduler_list]"

echo.
echo Testing IChingWuxing scheduler...
python313\python.exe -c "try: from genesis.custom_nodes.Comfyui.ComfyUI-WanVideoWrapper.wanvideo.schedulers.iching_wuxing_scheduler_core import IChingWuxingScheduler; print('✓ IChingWuxing scheduler available'); except ImportError as e: print(f'✗ IChingWuxing scheduler not available: {e}')"

echo.
pause
