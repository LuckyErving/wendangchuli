#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试承诺书文件是否能被正确识别和转换"""

import os
import re
import subprocess
from pathlib import Path

# 测试目录
test_dir = "/Users/ervin/Downloads/630222203210020071(李时海)"

print("=" * 60)
print("测试承诺书文件识别")
print("=" * 60)

# 1. 查找所有文件
print("\n1. 扫描目录中的所有文件...")
all_files = []
for root, dirs, filenames in os.walk(test_dir):
    for filename in filenames:
        if not filename.startswith('.'):
            filepath = os.path.join(root, filename)
            all_files.append(filepath)
            print(f"  找到: {filename}")

print(f"\n共找到 {len(all_files)} 个文件")

# 2. 测试承诺书识别
print("\n2. 测试承诺书关键字匹配...")
pattern = r'承诺书'
for filepath in all_files:
    filename = os.path.basename(filepath)
    if re.search(pattern, filename, re.IGNORECASE):
        print(f"\n✓ 匹配到承诺书: {filename}")
        print(f"  完整路径: {filepath}")
        print(f"  文件扩展名: {os.path.splitext(filepath)[1]}")
        print(f"  文件大小: {os.path.getsize(filepath)} 字节")
        print(f"  文件存在: {os.path.exists(filepath)}")
        
        # 3. 测试LibreOffice转换
        ext = os.path.splitext(filepath)[1].lower()
        if ext in ['.doc', '.docx']:
            print(f"\n3. 测试Word文档转换...")
            print(f"  检查LibreOffice是否安装...")
            
            # 检查soffice命令
            try:
                result = subprocess.run(['which', 'soffice'], 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=5)
                if result.returncode == 0:
                    soffice_path = result.stdout.strip()
                    print(f"  ✓ LibreOffice已安装: {soffice_path}")
                else:
                    print(f"  ✗ LibreOffice未安装或soffice命令不在PATH中")
                    print(f"  请安装LibreOffice: brew install --cask libreoffice")
                    continue
            except Exception as e:
                print(f"  ✗ 检查失败: {str(e)}")
                continue
            
            # 尝试转换
            output_dir = "/tmp/test_pdf"
            os.makedirs(output_dir, exist_ok=True)
            
            print(f"\n  尝试转换为PDF...")
            print(f"  输出目录: {output_dir}")
            
            try:
                result = subprocess.run(
                    ['soffice', '--headless', '--convert-to', 'pdf', 
                     '--outdir', output_dir, filepath],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                print(f"  返回码: {result.returncode}")
                if result.stdout:
                    print(f"  标准输出:\n{result.stdout}")
                if result.stderr:
                    print(f"  错误输出:\n{result.stderr}")
                
                # 检查输出文件
                expected_pdf = os.path.join(
                    output_dir,
                    os.path.splitext(os.path.basename(filepath))[0] + '.pdf'
                )
                print(f"\n  期望的PDF文件: {expected_pdf}")
                print(f"  PDF文件存在: {os.path.exists(expected_pdf)}")
                
                if os.path.exists(expected_pdf):
                    print(f"  PDF文件大小: {os.path.getsize(expected_pdf)} 字节")
                    print(f"  ✓ 转换成功!")
                else:
                    print(f"  ✗ 转换失败: PDF文件未生成")
                    # 列出输出目录的所有文件
                    print(f"\n  输出目录中的文件:")
                    for f in os.listdir(output_dir):
                        print(f"    - {f}")
                        
            except subprocess.TimeoutExpired:
                print(f"  ✗ 转换超时(30秒)")
            except Exception as e:
                print(f"  ✗ 转换出错: {str(e)}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
