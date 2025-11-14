@echo off
echo Quick Video Generation Test
echo.
echo This will test with minimal settings:
echo - 640x360 resolution
echo - 31 frames
echo - 4 steps
echo.

cd /d "%~dp0"

echo Starting...
python313\python.exe genesis\apps\wanvideo_gradio_app.py

pause
