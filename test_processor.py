#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试脚本 - 测试文档处理功能
"""

import os
import sys

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from document_processor import DocumentProcessor

def test_processor():
    """测试文档处理器"""
    print("=" * 60)
    print("文档处理器测试")
    print("=" * 60)
    
    # 创建处理器实例
    processor = DocumentProcessor()
    print("✓ DocumentProcessor 创建成功")
    
    # 测试文件夹路径
    test_folder = input("\n请输入测试文件夹路径: ").strip()
    
    if not test_folder:
        print("未输入路径，使用当前目录")
        test_folder = "."
    
    if not os.path.exists(test_folder):
        print(f"❌ 文件夹不存在: {test_folder}")
        return
    
    print(f"\n测试文件夹: {test_folder}")
    print("-" * 60)
    
    # 1. 查找文件
    print("\n[1] 查找文件...")
    try:
        files = processor.find_files(test_folder)
        print(f"✓ 找到 {len(files)} 个文件")
        for i, f in enumerate(files[:10], 1):  # 只显示前10个
            print(f"  {i}. {os.path.basename(f)}")
        if len(files) > 10:
            print(f"  ... 还有 {len(files) - 10} 个文件")
    except Exception as e:
        print(f"❌ 查找文件失败: {e}")
        return
    
    # 2. 分类文件
    print("\n[2] 分类文件...")
    try:
        classified = processor.sort_files(files)
        print("✓ 文件分类完成:")
        for doc_type, doc_files in classified.items():
            if doc_files:
                print(f"  {doc_type}: {len(doc_files)} 个")
                for f in doc_files[:3]:  # 显示前3个
                    print(f"    - {os.path.basename(f)}")
                if len(doc_files) > 3:
                    print(f"    ... 还有 {len(doc_files) - 3} 个")
    except Exception as e:
        print(f"❌ 分类文件失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 3. 测试转换（可选）
    print("\n[3] 是否测试完整处理流程？(y/n): ", end="")
    if input().strip().lower() == 'y':
        output_pdf = "test_output.pdf"
        print(f"\n开始处理，输出到: {output_pdf}")
        
        def progress_callback(value, message):
            print(f"  [{value}%] {message}")
        
        try:
            processor.process_folder(test_folder, output_pdf, progress_callback)
            print(f"\n✓ 处理完成！输出文件: {output_pdf}")
            print(f"  文件大小: {os.path.getsize(output_pdf) / 1024:.2f} KB")
        except Exception as e:
            print(f"\n❌ 处理失败: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_processor()
