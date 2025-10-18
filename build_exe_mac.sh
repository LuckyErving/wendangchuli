#!/bin/bash
# 文档处理器 - 打包为可执行文件 (macOS版本)

echo "================================"
echo "文档处理器 - 打包为可执行文件"
echo "================================"
echo ""

# 激活虚拟环境
if [ -f "/Users/ervin/Studio/zPlayground/.venv/bin/activate" ]; then
    echo "激活虚拟环境..."
    source /Users/ervin/Studio/zPlayground/.venv/bin/activate
else
    echo "错误: 找不到虚拟环境"
    exit 1
fi

# 检查 PyInstaller
echo ""
echo "检查 PyInstaller..."
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "安装 PyInstaller..."
    pip install pyinstaller
fi

# 清理旧文件
echo ""
echo "清理旧的打包文件..."
rm -rf build dist *.spec

# 打包
echo ""
echo "开始打包..."
echo "这可能需要几分钟时间..."
echo ""

pyinstaller --onefile \
    --windowed \
    --name="文档处理器" \
    --icon=NONE \
    --add-data="README.md:." \
    --hidden-import="PIL._tkinter_finder" \
    document_processor.py

if [ $? -eq 0 ]; then
    echo ""
    echo "================================"
    echo "打包成功！"
    echo "================================"
    echo ""
    echo "可执行文件位置: dist/文档处理器"
    echo ""
    echo "你可以将 dist/文档处理器 复制到任何Mac电脑上运行"
    echo ""
    
    # 询问是否运行
    read -p "是否现在运行？(y/n) " choice
    if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
        ./dist/文档处理器
    fi
else
    echo ""
    echo "================================"
    echo "打包失败，请检查错误信息"
    echo "================================"
    exit 1
fi

echo ""
read -p "按回车键退出..."
