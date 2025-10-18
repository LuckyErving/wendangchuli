@echo off
chcp 65001 >nul
echo ================================
echo 文档处理器 - 打包为可执行文件
echo ================================
echo.

REM 激活虚拟环境
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ❌ 虚拟环境不存在，请先运行 install_windows.bat
    pause
    exit /b 1
)

REM 检查PyInstaller是否已安装
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装PyInstaller...
    pip install pyinstaller
)

echo 正在打包程序...
echo.

REM 使用PyInstaller打包
pyinstaller --name="文档处理器" ^
    --onefile ^
    --windowed ^
    --icon=NONE ^
    --add-data="README.md;." ^
    --hidden-import=PIL ^
    --hidden-import=img2pdf ^
    --hidden-import=PyPDF2 ^
    --hidden-import=docx2pdf ^
    --hidden-import=win32com.client ^
    document_processor.py

echo.
if %errorlevel% equ 0 (
    echo ================================
    echo ✅ 打包成功！
    echo ================================
    echo.
    echo 可执行文件位置: dist\文档处理器.exe
    echo.
    echo 你可以将 dist\文档处理器.exe 复制到任何Windows电脑上运行
    echo 不需要安装Python环境
    echo.
) else (
    echo ================================
    echo ❌ 打包失败
    echo ================================
    echo.
)

pause
