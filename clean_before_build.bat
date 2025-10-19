@echo off
chcp 65001 >nul
REM 打包前清理脚本 - 用于清除开发时产生的授权记录

echo ==========================================
echo 文档处理器打包前清理
echo ==========================================
echo.

REM 清理授权记录
echo 1. 清理授权记录...
if exist "%APPDATA%\.docproc" (
    rmdir /s /q "%APPDATA%\.docproc"
    echo    ✅ 已删除授权配置: %%APPDATA%%\.docproc
) else (
    echo    ℹ️  授权配置不存在，跳过
)

REM 清理Python缓存
echo.
echo 2. 清理Python缓存...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
del /s /q *.pyc >nul 2>&1
echo    ✅ 已清理 __pycache__ 和 .pyc 文件

REM 清理旧的构建文件
echo.
echo 3. 清理旧的构建文件...
if exist "build" (
    rmdir /s /q "build"
    echo    ✅ 已删除 build 目录
)

if exist "dist" (
    rmdir /s /q "dist"
    echo    ✅ 已删除 dist 目录
)

echo.
echo ==========================================
echo 清理完成！现在可以开始打包了
echo ==========================================
echo.
echo 打包命令：
echo   Windows: build_exe.bat
echo.
pause
