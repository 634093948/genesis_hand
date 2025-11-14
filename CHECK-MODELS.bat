@echo off
echo ================================
echo   Checking Model Links
echo ================================
echo.

cd /d "%~dp0"

echo [1] Checking diffusion_models...
if exist "genesis\models\diffusion_models" (
    echo   OK - diffusion_models exists
    dir "genesis\models\diffusion_models" | findstr "SYMLINKD"
) else (
    echo   MISSING - diffusion_models not found!
)

echo.
echo [2] Checking unet...
if exist "genesis\models\unet" (
    echo   OK - unet exists
    dir "genesis\models\unet" | findstr "SYMLINKD"
) else (
    echo   MISSING - unet not found!
)

echo.
echo [3] Checking text_encoders...
if exist "genesis\models\text_encoders" (
    echo   OK - text_encoders exists
) else (
    echo   MISSING - text_encoders not found!
)

echo.
echo [4] Checking vae...
if exist "genesis\models\vae" (
    echo   OK - vae exists
) else (
    echo   MISSING - vae not found!
)

echo.
echo ================================
echo   Check Complete
echo ================================
pause
