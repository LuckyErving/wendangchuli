#!/bin/bash
# 方案3：准备给Windows用户的一键打包脚本
# 这个方案最简单实用：把源代码给Windows用户，让他们自己打包

echo "================================"
echo "准备Windows一键打包包"
echo "================================"
echo ""

OUTPUT_DIR="文档处理器_Windows一键打包版"
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

echo "正在准备文件..."

# 复制所有文件
cp document_processor.py "$OUTPUT_DIR/"
cp document_processor.spec "$OUTPUT_DIR/"
cp requirements.txt "$OUTPUT_DIR/"
cp README.md "$OUTPUT_DIR/"
cp install_windows.bat "$OUTPUT_DIR/"
cp run.bat "$OUTPUT_DIR/"
cp build_exe.bat "$OUTPUT_DIR/"

# 创建超级简单的一键安装打包脚本
cat > "$OUTPUT_DIR/一键安装并打包.bat" << 'EOF'
@echo off
chcp 65001 >nul
title 文档处理器 - 一键安装打包工具
color 0A

echo.
echo ========================================
echo    文档处理器 - 自动安装打包工具
echo ========================================
echo.
echo 此脚本将自动完成以下操作：
echo   1. 检查Python环境
echo   2. 创建虚拟环境
echo   3. 安装所有依赖
echo   4. 打包为exe可执行文件
echo.
echo 请耐心等待，整个过程需要5-10分钟
echo ========================================
echo.
pause

REM 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python！
    echo.
    echo 请先安装Python 3.7或更高版本
    echo 下载地址: https://www.python.org/downloads/
    echo.
    echo 安装时请勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo [1/4] ✓ Python环境检测通过
echo.

REM 创建虚拟环境
if not exist "venv" (
    echo [2/4] 正在创建虚拟环境...
    python -m venv venv
    echo       ✓ 虚拟环境创建完成
) else (
    echo [2/4] ✓ 虚拟环境已存在
)
echo.

REM 激活虚拟环境并安装依赖
echo [3/4] 正在安装依赖包（这可能需要几分钟）...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
pip install pyinstaller --quiet
echo       ✓ 依赖安装完成
echo.

REM 打包
echo [4/4] 正在打包为exe文件（这可能需要几分钟）...
pyinstaller --clean document_processor.spec
if %errorlevel% equ 0 (
    echo       ✓ 打包完成！
    echo.
    echo ========================================
    echo           🎉 全部完成！
    echo ========================================
    echo.
    echo 可执行文件位置:
    echo   %CD%\dist\文档处理器.exe
    echo.
    echo 使用方法:
    echo   1. 直接双击运行 dist\文档处理器.exe
    echo   2. 或将exe复制到其他电脑使用
    echo.
    start explorer dist
) else (
    echo       ✗ 打包失败
    echo.
    echo 请检查错误信息或联系开发者
    echo.
)

echo.
pause
EOF

# 创建更详细的说明文档
cat > "$OUTPUT_DIR/详细使用说明.txt" << 'EOF'
====================================================================
                    文档处理器 - 使用指南
====================================================================

📦 方式一：一键安装打包（最简单）
────────────────────────────────────────
1. 双击运行 "一键安装并打包.bat"
2. 等待5-10分钟自动完成所有步骤
3. 在 dist 文件夹找到 "文档处理器.exe"
4. 双击exe文件即可使用

注意：首次运行需要联网下载依赖包

🚀 方式二：直接运行（不打包）
────────────────────────────────────────
如果不需要打包为exe，可以直接运行：

1. 双击 "install_windows.bat"（仅第一次）
2. 双击 "run.bat" 开始使用

📋 功能说明
────────────────────────────────────────
自动将文件夹中的文档按指定顺序合并为一个PDF文件

支持文档类型：
• 申请书
• 户主声明书
• 承包方调查表
• 承包地块调查表
• 公示结果归户表
• 公示无异议声明书
• 土地承包合同书（自动输出4份副本）
• 登记簿
• 地块示意图（自动按编号排序）
• 确权登记声明书
• 承诺书

支持文件格式：
• 文档：PDF, DOC, DOCX
• 图片：JPG, JPEG, PNG, BMP, TIFF

💡 使用步骤
────────────────────────────────────────
1. 运行程序
2. 点击"浏览"选择包含文档的文件夹
3. 选择输出PDF的保存位置
4. 点击"开始处理"
5. 等待处理完成

⚠️ 系统要求
────────────────────────────────────────
• Windows 10/11
• Python 3.7+ （如果没有安装，请从 python.org 下载）
• 安装Python时必须勾选 "Add Python to PATH"

🔧 常见问题
────────────────────────────────────────
Q: 提示"找不到Python"？
A: 请从 https://www.python.org/downloads/ 下载安装Python
   安装时务必勾选 "Add Python to PATH"

Q: Word文档转换失败？
A: 会自动安装docx2pdf库，如果仍然失败，可能需要安装
   Microsoft Word或使用PDF格式的文档

Q: 打包后的exe很大？
A: 这是正常的，因为包含了Python运行环境和所有依赖库
   通常在50-100MB左右

Q: exe可以在其他电脑运行吗？
A: 可以！打包后的exe是独立的，可以复制到任何Windows电脑
   运行，不需要安装Python

📧 技术支持
────────────────────────────────────────
如有问题，请查看 README.md 获取更多信息

====================================================================
                      祝使用愉快！
====================================================================
EOF

# 创建快速开始指南
cat > "$OUTPUT_DIR/快速开始.txt" << 'EOF'
⚡ 快速开始指南
═══════════════════════════════════════

第一步：准备Python环境
─────────────────────────────
□ 检查是否安装Python（命令提示符输入: python --version）
□ 如果没有，从 https://www.python.org/downloads/ 下载安装
  ⚠️ 安装时必须勾选 "Add Python to PATH"

第二步：选择使用方式
─────────────────────────────
【方式A - 打包为exe（推荐）】
  → 双击 "一键安装并打包.bat"
  → 等待完成后，在 dist 文件夹找到 exe
  → 以后直接运行 exe，无需Python环境

【方式B - Python脚本运行】
  → 双击 "install_windows.bat"
  → 双击 "run.bat"

第三步：使用程序
─────────────────────────────
1. 准备一个包含所有文档的文件夹
2. 运行程序
3. 选择文件夹
4. 选择输出PDF位置
5. 点击"开始处理"

完成！
═══════════════════════════════════════
EOF

echo "✅ 文件准备完成"
echo ""

# 打包成zip
echo "正在创建压缩包..."
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_ZIP="${OUTPUT_DIR}_${TIMESTAMP}.zip"

if command -v zip &> /dev/null; then
    zip -r "$OUTPUT_ZIP" "$OUTPUT_DIR" -x "*.DS_Store" -x "__pycache__/*" -q
    echo "✅ 压缩包创建完成: $OUTPUT_ZIP"
else
    echo "⚠️  未找到zip命令"
fi

echo ""
echo "================================"
echo "✅ 准备完成！"
echo "================================"
echo ""
echo "📦 输出内容："
echo "   文件夹: $OUTPUT_DIR"
if [ -f "$OUTPUT_ZIP" ]; then
    echo "   压缩包: $OUTPUT_ZIP"
fi
echo ""
echo "📨 传输到Windows电脑后："
echo "   1. 解压文件"
echo "   2. 双击运行 '一键安装并打包.bat'"
echo "   3. 等待5-10分钟完成"
echo "   4. 在 dist 文件夹找到可执行文件"
echo ""

# 显示文件列表
ls -lh "$OUTPUT_DIR"
echo ""
