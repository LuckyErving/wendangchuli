#!/bin/bash
# 安装文档处理器所需的系统工具

echo "================================"
echo "文档处理器 - 依赖安装脚本"
echo "================================"
echo ""

# 检查Homebrew是否已安装
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew未安装"
    echo "请先安装Homebrew: https://brew.sh"
    exit 1
fi

echo "✅ Homebrew已安装"
echo ""

# 安装LibreOffice
echo "正在检查LibreOffice..."
if [ ! -d "/Applications/LibreOffice.app" ] && ! command -v soffice &> /dev/null; then
    echo "正在安装LibreOffice（用于转换Word文档）..."
    brew install --cask libreoffice
    echo "✅ LibreOffice安装完成"
else
    echo "✅ LibreOffice已安装"
    
    # 检查soffice命令是否可用
    if ! command -v soffice &> /dev/null; then
        echo "正在创建soffice软链接..."
        if [ -f "/Applications/LibreOffice.app/Contents/MacOS/soffice" ]; then
            sudo ln -sf /Applications/LibreOffice.app/Contents/MacOS/soffice /usr/local/bin/soffice
            echo "✅ soffice命令已配置"
        fi
    fi
fi
echo ""

# 激活虚拟环境并安装Python依赖
echo "正在安装Python依赖..."
source /Users/ervin/Studio/zPlayground/.venv/bin/activate
pip install -r requirements.txt
echo "✅ Python依赖安装完成"
echo ""

echo "================================"
echo "✅ 所有依赖安装完成！"
echo "================================"
echo ""
echo "使用方法："
echo "  source /Users/ervin/Studio/zPlayground/.venv/bin/activate"
echo "  python document_processor.py"
echo ""
