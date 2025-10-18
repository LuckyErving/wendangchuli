#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档处理器 - 简化测试版本
"""

import tkinter as tk
from tkinter import ttk
import os

# 消除macOS的Tk废弃警告
os.environ['TK_SILENCE_DEPRECATION'] = '1'

def test_ui():
    """测试UI显示"""
    root = tk.Tk()
    root.title("测试窗口")
    root.geometry("400x300")
    root.configure(bg='white')
    
    # 创建标签
    label = tk.Label(root, text="如果你能看到这个文字，说明tkinter正常工作", 
                     font=('Arial', 14), bg='white', fg='black')
    label.pack(pady=50)
    
    # 创建按钮
    button = tk.Button(root, text="点击测试", command=lambda: print("按钮工作正常"))
    button.pack(pady=20)
    
    # 创建ttk组件
    ttk_label = ttk.Label(root, text="这是ttk标签")
    ttk_label.pack(pady=10)
    
    ttk_button = ttk.Button(root, text="TTK按钮")
    ttk_button.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    print("正在启动测试窗口...")
    test_ui()
