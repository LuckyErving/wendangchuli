#!/bin/bash
# 使用Docker在Mac上打包Windows可执行文件
# 注意：此方法较复杂，推荐使用GitHub Actions方案

echo "================================"
echo "Docker + Wine 打包方案"
echo "================================"
echo ""
echo "此方法需要安装Docker Desktop for Mac"
echo ""

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装"
    echo "请先安装Docker Desktop: https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo "✅ Docker已安装"
echo ""

# 创建Dockerfile
cat > Dockerfile.windows << 'EOF'
FROM cdrx/pyinstaller-windows:python3

WORKDIR /src

# 复制项目文件
COPY requirements.txt .
COPY document_processor.py .
COPY document_processor.spec .

# 安装依赖
RUN pip install -r requirements.txt

# 打包
RUN pyinstaller document_processor.spec

# 输出目录
CMD ["cp", "-r", "dist", "/output/"]
EOF

echo "正在构建Docker镜像..."
docker build -f Dockerfile.windows -t doc-processor-builder .

echo "正在打包Windows可执行文件..."
mkdir -p dist_windows
docker run --rm -v "$(pwd)/dist_windows:/output" doc-processor-builder

echo ""
echo "================================"
echo "✅ 打包完成！"
echo "================================"
echo "输出位置: dist_windows/"
echo ""

# 清理
rm Dockerfile.windows
