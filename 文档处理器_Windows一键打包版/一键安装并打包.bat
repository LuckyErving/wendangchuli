@echo off
chcp 65001 >nul
title 文档处理器 - 一键安装打包工具
color 0A

echo.
echo ========================================
echo    文档处理器 - 自动安装打包工具
echo ========================================
echo.
echo 此脚本将自动完成以下操作：
echo   1. 检查Python环境
echo   2. 创建虚拟环境
echo   3. 安装所有依赖
echo   4. 打包为exe可执行文件
echo.
echo 请耐心等待，整个过程需要5-10分钟
echo ========================================
echo.
pause

REM 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python！
    echo.
    echo 请先安装Python 3.7或更高版本
    echo 下载地址: https://www.python.org/downloads/
    echo.
    echo 安装时请勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo [1/4] ✓ Python环境检测通过
echo.

REM 创建虚拟环境
if not exist "venv" (
    echo [2/4] 正在创建虚拟环境...
    python -m venv venv
    echo       ✓ 虚拟环境创建完成
) else (
    echo [2/4] ✓ 虚拟环境已存在
)
echo.

REM 激活虚拟环境并安装依赖
echo [3/4] 正在安装依赖包（这可能需要几分钟）...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
pip install pyinstaller --quiet
echo       ✓ 依赖安装完成
echo.

REM 打包
echo [4/4] 正在打包为exe文件（这可能需要几分钟）...
pyinstaller --clean document_processor.spec
if %errorlevel% equ 0 (
    echo       ✓ 打包完成！
    echo.
    echo ========================================
    echo           🎉 全部完成！
    echo ========================================
    echo.
    echo 可执行文件位置:
    echo   %CD%\dist\文档处理器.exe
    echo.
    echo 使用方法:
    echo   1. 直接双击运行 dist\文档处理器.exe
    echo   2. 或将exe复制到其他电脑使用
    echo.
    start explorer dist
) else (
    echo       ✗ 打包失败
    echo.
    echo 请检查错误信息或联系开发者
    echo.
)

echo.
pause
