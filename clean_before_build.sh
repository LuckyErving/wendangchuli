#!/bin/bash
# 打包前清理脚本 - 用于清除开发时产生的授权记录

echo "=========================================="
echo "文档处理器打包前清理"
echo "=========================================="
echo ""

# 清理授权记录
echo "1. 清理授权记录..."
if [ -d "$HOME/.docproc" ]; then
    rm -rf "$HOME/.docproc"
    echo "   ✅ 已删除授权配置: ~/.docproc"
else
    echo "   ℹ️  授权配置不存在，跳过"
fi

# 清理Python缓存
echo ""
echo "2. 清理Python缓存..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
echo "   ✅ 已清理 __pycache__ 和 .pyc 文件"

# 清理旧的构建文件
echo ""
echo "3. 清理旧的构建文件..."
if [ -d "build" ]; then
    rm -rf build
    echo "   ✅ 已删除 build 目录"
fi

if [ -d "dist" ]; then
    rm -rf dist
    echo "   ✅ 已删除 dist 目录"
fi

# 清理spec文件（如果需要重新生成）
# if [ -f "文档处理器.spec" ]; then
#     rm "文档处理器.spec"
#     echo "   ✅ 已删除 spec 文件"
# fi

echo ""
echo "=========================================="
echo "清理完成！现在可以开始打包了"
echo "=========================================="
echo ""
echo "打包命令："
echo "  macOS:   ./build_exe_mac.sh"
echo "  Windows: build_exe.bat"
echo ""
