@echo off
chcp 65001 >nul
echo ========================================
echo Windows 保存验证测试
echo ========================================
echo.

echo [1] 检查 Python 环境
python --version
if errorlevel 1 (
    echo ❌ Python 未安装或未添加到PATH
    pause
    exit /b 1
)
echo.

echo [2] 检查 APPDATA 环境变量
echo APPDATA = %APPDATA%
if "%APPDATA%"=="" (
    echo ❌ APPDATA 环境变量未设置
    pause
    exit /b 1
)
echo.

echo [3] 检查配置目录权限
set CONFIG_DIR=%APPDATA%\.docproc
echo 配置目录: %CONFIG_DIR%

if not exist "%CONFIG_DIR%" (
    echo 目录不存在，尝试创建...
    mkdir "%CONFIG_DIR%"
    if errorlevel 1 (
        echo ❌ 无法创建目录
        pause
        exit /b 1
    )
    echo ✅ 目录创建成功
) else (
    echo ✅ 目录已存在
)
echo.

echo [4] 测试文件写入权限
set TEST_FILE=%CONFIG_DIR%\test.txt
echo test > "%TEST_FILE%"
if errorlevel 1 (
    echo ❌ 无法写入文件
    pause
    exit /b 1
)
echo ✅ 写入权限正常
del "%TEST_FILE%"
echo.

echo [5] 运行 Python 测试脚本
python test_save_verify.py
if errorlevel 1 (
    echo ❌ 测试失败
    pause
    exit /b 1
)
echo.

echo ========================================
echo ✅✅✅ 所有测试通过！
echo ========================================
pause
