#!/bin/bash
# 代码混淆和打包脚本

echo "================================"
echo "文档处理器 - 代码保护打包工具"
echo "================================"
echo ""

# 检查PyArmor是否安装
if ! python -c "import pyarmor" 2>/dev/null; then
    echo "正在安装 PyArmor..."
    pip install pyarmor
fi

# 清理之前的输出
echo "清理旧文件..."
rm -rf dist_protected/
rm -rf build/
rm -rf dist/

# 创建输出目录
mkdir -p dist_protected

echo ""
echo "步骤 1/3: 使用 PyArmor 混淆代码..."
echo "----------------------------------------"

# 混淆主程序和授权模块
pyarmor gen --output dist_protected --recursive document_processor.py
pyarmor gen --output dist_protected --recursive license_manager.py

# 检查混淆是否成功
if [ ! -f "dist_protected/document_processor.py" ]; then
    echo "❌ 混淆失败！"
    exit 1
fi

echo "✅ 代码混淆完成"
echo ""

# 复制其他必要文件
echo "步骤 2/3: 复制资源文件..."
echo "----------------------------------------"
cp requirements.txt dist_protected/ 2>/dev/null || echo "⚠️  requirements.txt 不存在"
cp README.md dist_protected/ 2>/dev/null || echo "⚠️  README.md 不存在"

# 复制文档
if [ -d "docs" ]; then
    cp -r docs dist_protected/
    echo "✅ 文档已复制"
fi

echo ""
echo "步骤 3/3: 准备打包配置..."
echo "----------------------------------------"

# 创建PyInstaller配置文件
cat > dist_protected/document_processor.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['document_processor.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('pyarmor_runtime_000000', 'pyarmor_runtime_000000'),
    ],
    hiddenimports=[
        'license_manager',
        'PIL._tkinter_finder',
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='文档处理器',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 无控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加图标路径
)
EOF

echo "✅ PyInstaller 配置文件已创建"
echo ""

echo "================================"
echo "✅ 代码保护完成！"
echo "================================"
echo ""
echo "混淆后的文件位于: dist_protected/"
echo ""
echo "📦 下一步打包成 EXE："
echo "1. cd dist_protected"
echo "2. pip install -r requirements.txt"
echo "3. pyinstaller document_processor.spec"
echo ""
echo "⚠️  重要提示："
echo "- 混淆后的代码反编译后将显示为乱码"
echo "- 程序已绑定设备MAC地址，无法在其他机器运行"
echo "- 每个设备限制使用200次"
echo "- 达到限制后将显示'程序已损坏'错误"
echo ""
