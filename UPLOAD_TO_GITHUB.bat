@echo off
chcp 65001 >nul
cd /d "%~dp0"
title GitHub 上传助手
color 0A

echo.
echo ========================================
echo   GitHub 上传助手
echo ========================================
echo.

REM 检查是否已初始化
if not exist ".git" (
    echo [1/6] 初始化 Git 仓库...
    git init
    echo 完成
    echo.
) else (
    echo [1/6] Git 仓库已存在
    echo.
)

REM 配置 Git 用户信息
echo [2/6] 配置 Git 用户信息
echo.
set /p USERNAME="请输入你的 GitHub 用户名: "
set /p EMAIL="请输入你的 GitHub 邮箱: "

git config user.name "%USERNAME%"
git config user.email "%EMAIL%"
echo 配置完成
echo.

REM 添加文件
echo [3/6] 添加文件到 Git...
git add .
echo 完成
echo.

REM 提交
echo [4/6] 提交更改...
set /p COMMIT_MSG="请输入提交信息 (默认: Initial commit): "
if "%COMMIT_MSG%"=="" set COMMIT_MSG=Initial commit
git commit -m "%COMMIT_MSG%"
echo 完成
echo.

REM 添加远程仓库
echo [5/6] 添加远程仓库
echo.
echo 请先在 GitHub 上创建一个新仓库（不要初始化 README）
echo 仓库名建议: genesis_hand 或 wanvideo-genesis
echo.
set /p REPO_URL="请输入仓库 URL (格式: https://github.com/用户名/仓库名.git): "

git remote remove origin 2>nul
git remote add origin %REPO_URL%
echo 完成
echo.

REM 推送
echo [6/6] 推送到 GitHub...
echo.
echo 注意: 如果是第一次推送，可能需要输入 GitHub 用户名和密码
echo 或者使用 Personal Access Token
echo.
pause

git branch -M main
git push -u origin main

echo.
echo ========================================
echo   上传完成！
echo ========================================
echo.
echo 仓库地址: %REPO_URL%
echo.
echo 下一步:
echo 1. 访问 GitHub 仓库
echo 2. 创建 Release
echo 3. 上传大文件（genesis.zip, python313.zip）到 Release
echo.
pause
