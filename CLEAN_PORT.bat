@echo off
chcp 65001 >nul
title Clean Port 7860
color 0C

echo.
echo ========================================
echo   Cleaning Port 7860
echo ========================================
echo.

echo Finding processes using port 7860...
netstat -ano | findstr :7860

echo.
echo Killing all processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :7860') do (
    echo Killing PID: %%a
    taskkill /F /PID %%a
)

echo.
echo ========================================
echo   Port 7860 cleaned!
echo ========================================
echo.

pause
