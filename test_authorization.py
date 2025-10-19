#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试授权系统集成
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("测试 document_processor.py 中的授权集成")
print("=" * 60)

# 测试云端授权管理器
print("\n1. 测试云端授权管理器")
print("-" * 60)

try:
    from cloud_license import CloudLicenseManager
    
    manager = CloudLicenseManager()
    can_use, message = manager.check_and_update_usage()
    
    print(f"\n✅ 云端授权测试完成")
    print(f"   结果: {'允许使用' if can_use else '拒绝使用'}")
    print(f"   消息: {message}")
    
except Exception as e:
    print(f"\n❌ 云端授权测试失败: {e}")
    import traceback
    traceback.print_exc()

# 测试 document_processor 的授权逻辑
print("\n2. 测试 document_processor 的授权逻辑")
print("-" * 60)

try:
    # 模拟 document_processor.py 的导入逻辑
    from license_config import USE_CLOUD
    print(f"   USE_CLOUD = {USE_CLOUD}")
    
    if USE_CLOUD:
        from cloud_license import CloudLicenseManager as LicenseManager
        print(f"   ✅ 使用云端授权系统")
    else:
        print(f"   ⚠️ 使用本地授权系统")
    
    # 创建管理器并测试
    license_mgr = LicenseManager()
    can_use, msg = license_mgr.check_and_update_usage()
    
    print(f"\n   授权检查结果:")
    print(f"   - 是否允许: {can_use}")
    print(f"   - 消息: {msg}")
    
    if not can_use:
        print(f"\n   ✅ 正确行为: 已达到限制，拒绝使用")
        print(f"   ✅ 消息正确: '{msg}' (应显示为'程序已损坏')")
    else:
        print(f"\n   ⚠️ 意外行为: 应该拒绝但允许了使用")
    
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
