#!/bin/bash
# Mac上运行文档处理器

# 激活虚拟环境
source /Users/ervin/Studio/zPlayground/.venv/bin/activate

# 设置环境变量消除警告
export TK_SILENCE_DEPRECATION=1

# 运行程序
cd /Users/ervin/Studio/zPlayground/part-time/wendangchuli
python document_processor.py
