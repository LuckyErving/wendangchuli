@echo off
chcp 65001 >nul
echo ================================
echo 文档处理器 - Windows依赖安装脚本
echo ================================
echo.

REM 检查Python是否已安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装
    echo 请先安装Python 3.7或更高版本: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python已安装
echo.

REM 创建虚拟环境（如果不存在）
if not exist "venv" (
    echo 正在创建虚拟环境...
    python -m venv venv
    echo ✅ 虚拟环境创建完成
) else (
    echo ✅ 虚拟环境已存在
)
echo.

REM 激活虚拟环境并安装依赖
echo 正在安装Python依赖...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
echo ✅ Python依赖安装完成
echo.

REM 检查WinRAR是否已安装
if exist "C:\Program Files\WinRAR\WinRAR.exe" (
    echo ✅ WinRAR已安装
) else if exist "C:\Program Files (x86)\WinRAR\WinRAR.exe" (
    echo ✅ WinRAR已安装
) else (
    echo ⚠️  WinRAR未安装
    echo 建议安装WinRAR: https://www.winrar.com/
    echo 或者已经安装了rarfile库作为替代
)
echo.

echo ================================
echo ✅ 安装完成！
echo ================================
echo.
echo 使用方法：
echo   1. 双击运行: run.bat
echo   或
echo   2. 命令行运行:
echo      call venv\Scripts\activate.bat
echo      python document_processor.py
echo.
pause
