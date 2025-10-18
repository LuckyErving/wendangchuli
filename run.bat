@echo off
chcp 65001 >nul
echo 正在启动文档处理器...
call venv\Scripts\activate.bat
python document_processor.py
pause
