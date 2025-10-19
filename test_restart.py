#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试关闭重启场景
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from document_processor import LicenseManager

def test_restart():
    """测试关闭重启场景"""
    print("=" * 60)
    print("测试场景：关闭exe后重新打开")
    print("=" * 60)
    
    # 模拟第一次运行
    print("\n【第一次运行程序】")
    manager1 = LicenseManager()
    
    print("1. 程序启动 - 检查设备")
    can_use, msg = manager1.check_device()
    print(f"   {manager1.get_usage_info()}")
    
    print("\n2. 处理第1个文档")
    can_use, msg = manager1.check_and_update_usage()
    print(f"   {msg}")
    print(f"   {manager1.get_usage_info()}")
    
    print("\n3. 处理第2个文档")
    can_use, msg = manager1.check_and_update_usage()
    print(f"   {msg}")
    print(f"   {manager1.get_usage_info()}")
    
    print("\n4. 处理第3个文档")
    can_use, msg = manager1.check_and_update_usage()
    print(f"   {msg}")
    print(f"   {manager1.get_usage_info()}")
    
    print("\n[用户关闭程序]")
    del manager1  # 模拟程序关闭
    
    # 模拟重新打开程序
    print("\n" + "=" * 60)
    print("【重新打开程序】")
    manager2 = LicenseManager()
    
    print("1. 程序启动 - 检查设备")
    can_use, msg = manager2.check_device()
    print(f"   {manager2.get_usage_info()}")
    print(f"   ⚠️  注意：次数应该是累计的，不应该重置！")
    
    print("\n2. 处理第4个文档")
    can_use, msg = manager2.check_and_update_usage()
    print(f"   {msg}")
    print(f"   {manager2.get_usage_info()}")
    
    print("\n3. 处理第5个文档")
    can_use, msg = manager2.check_and_update_usage()
    print(f"   {msg}")
    print(f"   {manager2.get_usage_info()}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
    
    # 验证
    usage_data = manager2.load_usage_data()
    final_count = usage_data.get('count', 0)
    print(f"\n最终使用次数: {final_count}")
    print(f"预期次数: 5")
    
    if final_count == 5:
        print("✅ 正确：关闭重启后次数累计正常")
    else:
        print(f"❌ 错误：次数应该是5，实际是{final_count}")

if __name__ == "__main__":
    test_restart()
