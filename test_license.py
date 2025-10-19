#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试授权系统
"""

import sys
import os

# 将当前目录添加到路径
sys.path.insert(0, os.path.dirname(__file__))

from document_processor import LicenseManager

def test_license():
    """测试授权管理器"""
    print("=" * 60)
    print("授权系统测试")
    print("=" * 60)
    
    manager = LicenseManager()
    
    # 获取MAC地址
    mac = manager.get_mac_address()
    print(f"\n当前设备MAC地址: {mac}")
    
    # 获取设备哈希
    device_hash = manager._get_device_hash(mac)
    print(f"设备指纹哈希: {device_hash[:16]}...")
    
    # 获取使用信息
    usage_info = manager.get_usage_info()
    print(f"\n{usage_info}")
    
    # 加载使用数据
    usage_data = manager.load_usage_data()
    if usage_data:
        print(f"\n详细信息:")
        print(f"  - 使用次数: {usage_data.get('count', 0)}")
        print(f"  - 首次使用: {usage_data.get('first_use', 'N/A')}")
        print(f"  - 最近使用: {usage_data.get('last_use', 'N/A')}")
        print(f"  - 设备绑定: {usage_data.get('device', 'N/A')[:16]}...")
    
    print("\n" + "=" * 60)
    
    # 测试检查功能（不会真的增加次数，因为已经在初始化时增加过）
    can_use, message = manager.check_and_update_usage()
    print(f"\n授权检查结果:")
    print(f"  - 是否可用: {'✅ 是' if can_use else '❌ 否'}")
    print(f"  - 消息: {message}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

def reset_license():
    """重置授权（仅用于测试）"""
    import shutil
    manager = LicenseManager()
    
    if os.path.exists(manager.config_dir):
        response = input(f"\n确定要删除授权文件吗？({manager.config_dir}) [y/N]: ")
        if response.lower() == 'y':
            shutil.rmtree(manager.config_dir)
            print("✅ 授权文件已删除")
        else:
            print("❌ 取消操作")
    else:
        print("⚠️  授权文件不存在")

def simulate_usage(count=5):
    """模拟使用N次"""
    manager = LicenseManager()
    print(f"\n开始模拟使用 {count} 次...")
    
    for i in range(count):
        can_use, message = manager.check_and_update_usage()
        print(f"第 {i+1} 次: {message}")
        if not can_use:
            print(f"❌ 在第 {i+1} 次时被阻止")
            break
    
    print(f"\n最终状态: {manager.get_usage_info()}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='授权系统测试工具')
    parser.add_argument('--reset', action='store_true', help='重置授权')
    parser.add_argument('--simulate', type=int, metavar='N', help='模拟使用N次')
    
    args = parser.parse_args()
    
    if args.reset:
        reset_license()
    elif args.simulate:
        simulate_usage(args.simulate)
    else:
        test_license()
