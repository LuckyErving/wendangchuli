#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试：验证使用次数计数
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from document_processor import LicenseManager

def simple_test():
    """简单测试计数功能"""
    print("=" * 60)
    print("简单计数测试")
    print("=" * 60)
    
    manager = LicenseManager()
    
    print("\n初始状态:")
    print(f"  {manager.get_usage_info()}")
    
    for i in range(1, 6):
        print(f"\n第 {i} 次处理文档:")
        can_use, msg = manager.check_and_update_usage()
        if can_use:
            print(f"  ✅ 允许处理")
            print(f"  消息: {msg}")
            print(f"  状态: {manager.get_usage_info()}")
        else:
            print(f"  ❌ 拒绝处理")
            print(f"  消息: {msg}")
            break
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
    # 显示配置文件内容
    usage_data = manager.load_usage_data()
    if usage_data:
        print("\n配置文件内容:")
        import json
        print(json.dumps(usage_data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    simple_test()
