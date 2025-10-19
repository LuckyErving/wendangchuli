@echo off
REM Windows版本 - 代码混淆和打包脚本
chcp 65001 >nul

echo ================================
echo 文档处理器 - 代码保护打包工具
echo ================================
echo.

REM 检查PyArmor是否安装
python -c "import pyarmor" 2>nul
if errorlevel 1 (
    echo 正在安装 PyArmor...
    pip install pyarmor
)

REM 清理之前的输出
echo 清理旧文件...
if exist dist_protected rmdir /s /q dist_protected
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM 创建输出目录
mkdir dist_protected

echo.
echo 步骤 1/3: 使用 PyArmor 混淆代码...
echo ----------------------------------------

REM 混淆主程序和授权模块
pyarmor gen --output dist_protected --recursive document_processor.py
pyarmor gen --output dist_protected --recursive license_manager.py

REM 检查混淆是否成功
if not exist "dist_protected\document_processor.py" (
    echo ❌ 混淆失败！
    exit /b 1
)

echo ✅ 代码混淆完成
echo.

REM 复制其他必要文件
echo 步骤 2/3: 复制资源文件...
echo ----------------------------------------
copy requirements.txt dist_protected\ 2>nul
copy README.md dist_protected\ 2>nul

REM 复制文档
if exist docs xcopy docs dist_protected\docs\ /E /I /Y >nul

echo.
echo 步骤 3/3: 准备打包配置...
echo ----------------------------------------

REM 创建PyInstaller配置文件
(
echo # -*- mode: python ; coding: utf-8 -*-
echo.
echo block_cipher = None
echo.
echo a = Analysis^(
echo     ['document_processor.py'],
echo     pathex=[],
echo     binaries=[],
echo     datas=[
echo         ^('pyarmor_runtime_000000', 'pyarmor_runtime_000000'^),
echo     ],
echo     hiddenimports=[
echo         'license_manager',
echo         'PIL._tkinter_finder',
echo         'tkinter',
echo         'tkinter.filedialog',
echo         'tkinter.messagebox',
echo     ],
echo     hookspath=[],
echo     hooksconfig={},
echo     runtime_hooks=[],
echo     excludes=[],
echo     win_no_prefer_redirects=False,
echo     win_private_assemblies=False,
echo     cipher=block_cipher,
echo     noarchive=False,
echo ^)
echo.
echo pyz = PYZ^(a.pure, a.zipped_data, cipher=block_cipher^)
echo.
echo exe = EXE^(
echo     pyz,
echo     a.scripts,
echo     a.binaries,
echo     a.zipfiles,
echo     a.datas,
echo     [],
echo     name='文档处理器',
echo     debug=False,
echo     bootloader_ignore_signals=False,
echo     strip=False,
echo     upx=True,
echo     upx_exclude=[],
echo     runtime_tmpdir=None,
echo     console=False,
echo     disable_windowed_traceback=False,
echo     argv_emulation=False,
echo     target_arch=None,
echo     codesign_identity=None,
echo     entitlements_file=None,
echo     icon=None,
echo ^)
) > dist_protected\document_processor.spec

echo ✅ PyInstaller 配置文件已创建
echo.

echo ================================
echo ✅ 代码保护完成！
echo ================================
echo.
echo 混淆后的文件位于: dist_protected\
echo.
echo 📦 下一步打包成 EXE：
echo 1. cd dist_protected
echo 2. pip install -r requirements.txt
echo 3. pyinstaller document_processor.spec
echo.
echo ⚠️  重要提示：
echo - 混淆后的代码反编译后将显示为乱码
echo - 程序已绑定设备MAC地址，无法在其他机器运行
echo - 每个设备限制使用200次
echo - 达到限制后将显示'程序已损坏'错误
echo.
pause
