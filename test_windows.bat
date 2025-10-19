@echo off
chcp 65001 >nul
REM Windows授权测试脚本

echo ==========================================
echo 授权系统诊断工具（Windows）
echo ==========================================
echo.

echo [步骤1] 检查Python环境
python --version
if %errorlevel% neq 0 (
    echo ❌ Python未安装或不在PATH中
    pause
    exit /b 1
)
echo.

echo [步骤2] 检查配置目录
echo APPDATA目录: %APPDATA%
if exist "%APPDATA%\.docproc" (
    echo ✅ 配置目录存在: %APPDATA%\.docproc
    dir "%APPDATA%\.docproc"
) else (
    echo ⚠️  配置目录不存在
)
echo.

echo [步骤3] 运行授权测试
python test_simple.py
echo.

echo [步骤4] 检查配置文件
if exist "%APPDATA%\.docproc\.lic" (
    echo ✅ 配置文件存在
    echo 文件大小:
    dir "%APPDATA%\.docproc\.lic" | find ".lic"
    echo.
    echo 文件内容（前100字符）:
    type "%APPDATA%\.docproc\.lic" | more +1 /e +100
) else (
    echo ❌ 配置文件不存在！这可能是问题所在。
)
echo.

echo ==========================================
echo 测试完成
echo ==========================================
pause
