#!/bin/bash
# 在Mac上准备Windows部署包

echo "================================"
echo "准备Windows部署包"
echo "================================"
echo ""

# 设置输出目录
OUTPUT_DIR="文档处理器_Windows部署包"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_ZIP="${OUTPUT_DIR}_${TIMESTAMP}.zip"

# 创建临时目录
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

echo "正在复制项目文件..."

# 复制必要的文件
cp document_processor.py "$OUTPUT_DIR/"
cp document_processor.spec "$OUTPUT_DIR/"
cp requirements.txt "$OUTPUT_DIR/"
cp README.md "$OUTPUT_DIR/"
cp install_windows.bat "$OUTPUT_DIR/"
cp run.bat "$OUTPUT_DIR/"
cp build_exe.bat "$OUTPUT_DIR/"

# 创建使用说明
cat > "$OUTPUT_DIR/使用说明.txt" << 'EOF'
文档处理器 - Windows部署说明
================================

这是从Mac开发环境准备的Windows部署包。

快速开始：
---------
1. 解压整个文件夹到Windows电脑
2. 双击运行 "install_windows.bat" 安装依赖
3. 选择以下任一方式使用：

   方式A：直接运行（推荐）
   - 双击 "run.bat" 即可使用

   方式B：打包为独立exe
   - 双击 "build_exe.bat"
   - 等待打包完成
   - 在 dist 文件夹找到 "文档处理器.exe"
   - 可以将exe复制到其他电脑使用

系统要求：
---------
- Windows 10/11
- Python 3.7+ (首次运行会自动创建虚拟环境)

功能说明：
---------
自动将文件夹中的文档按以下顺序合并为PDF：

1. 申请书
2. 户主声明书
3. 承包方调查表
4. 承包地块调查表
5. 公示结果归户表
6. 公示无异议声明书
7. 土地承包合同书（自动输出4份）
8. 登记簿
9. 地块示意图（按DKSYT编号排序）
10. 确权登记声明书
11. 承诺书

支持格式：
---------
- 文档：PDF, DOC, DOCX
- 图片：JPG, JPEG, PNG, BMP, TIFF

详细说明请查看 README.md

================================
开发者：文档处理器
日期：$(date +"%Y-%m-%d")
================================
EOF

echo "✅ 文件复制完成"
echo ""

# 创建zip压缩包
echo "正在创建压缩包..."
if command -v zip &> /dev/null; then
    zip -r "$OUTPUT_ZIP" "$OUTPUT_DIR" -x "*.DS_Store" -x "__pycache__/*"
    echo "✅ 压缩包创建完成: $OUTPUT_ZIP"
else
    echo "⚠️  未找到zip命令，跳过压缩"
    echo "你可以手动压缩 '$OUTPUT_DIR' 文件夹"
fi

echo ""
echo "================================"
echo "✅ Windows部署包准备完成！"
echo "================================"
echo ""
echo "下一步："
echo "1. 将 '$OUTPUT_DIR' 文件夹（或 $OUTPUT_ZIP）传输到Windows电脑"
echo "2. 在Windows上解压并运行 install_windows.bat"
echo "3. 运行 run.bat 或 build_exe.bat"
echo ""
echo "文件清单："
ls -lh "$OUTPUT_DIR"
echo ""
