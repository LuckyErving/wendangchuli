#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试使用次数流程
"""

import sys
import os

# 将当前目录添加到路径
sys.path.insert(0, os.path.dirname(__file__))

from document_processor import LicenseManager

def test_usage_flow():
    """测试完整的使用流程"""
    print("=" * 60)
    print("测试使用次数流程")
    print("=" * 60)
    
    manager = LicenseManager()
    
    # 1. 模拟程序启动 - 只检查设备，不计数
    print("\n【步骤1】程序启动 - 检查设备绑定")
    can_use, message = manager.check_device()
    print(f"  结果: {'✅ 允许' if can_use else '❌ 拒绝'}")
    print(f"  消息: {message}")
    print(f"  当前状态: {manager.get_usage_info()}")
    
    # 2. 模拟第一次处理文档 - 检查并计数
    print("\n【步骤2】第一次处理文档 - 检查并更新计数")
    can_use, message = manager.check_and_update_usage()
    print(f"  结果: {'✅ 允许' if can_use else '❌ 拒绝'}")
    print(f"  消息: {message}")
    print(f"  当前状态: {manager.get_usage_info()}")
    
    # 3. 模拟第二次处理文档
    print("\n【步骤3】第二次处理文档 - 检查并更新计数")
    can_use, message = manager.check_and_update_usage()
    print(f"  结果: {'✅ 允许' if can_use else '❌ 拒绝'}")
    print(f"  消息: {message}")
    print(f"  当前状态: {manager.get_usage_info()}")
    
    # 4. 模拟第三次处理文档
    print("\n【步骤4】第三次处理文档 - 检查并更新计数")
    can_use, message = manager.check_and_update_usage()
    print(f"  结果: {'✅ 允许' if can_use else '❌ 拒绝'}")
    print(f"  消息: {message}")
    print(f"  当前状态: {manager.get_usage_info()}")
    
    # 5. 模拟程序重启 - 只检查设备
    print("\n【步骤5】程序重启 - 再次检查设备绑定（不增加计数）")
    can_use, message = manager.check_device()
    print(f"  结果: {'✅ 允许' if can_use else '❌ 拒绝'}")
    print(f"  消息: {message}")
    print(f"  当前状态: {manager.get_usage_info()}")
    
    # 6. 重启后处理文档
    print("\n【步骤6】重启后第一次处理文档")
    can_use, message = manager.check_and_update_usage()
    print(f"  结果: {'✅ 允许' if can_use else '❌ 拒绝'}")
    print(f"  消息: {message}")
    print(f"  当前状态: {manager.get_usage_info()}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
    
    # 显示详细信息
    usage_data = manager.load_usage_data()
    if usage_data:
        print("\n详细使用记录:")
        print(f"  - 总使用次数: {usage_data.get('count', 0)}")
        print(f"  - 首次使用: {usage_data.get('first_use', 'N/A')}")
        print(f"  - 最近使用: {usage_data.get('last_use', 'N/A')}")

if __name__ == "__main__":
    test_usage_flow()
