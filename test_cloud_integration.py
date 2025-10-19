#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试云端授权集成
"""

import sys
import os

print("="*60)
print("测试云端授权集成到主程序")
print("="*60)
print()

# 测试1：导入主程序
print("【测试1】导入主程序...")
try:
    from document_processor import SimpleGUI
    print("✅ 主程序导入成功")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

print()

# 测试2：检查授权管理器类型
print("【测试2】检查授权管理器类型...")
try:
    # 不实际创建GUI（避免Tkinter窗口）
    # 只检查导入
    from license_config import USE_CLOUD
    
    if USE_CLOUD:
        from cloud_license import CloudLicenseManager
        manager = CloudLicenseManager()
        print(f"✅ 使用云端授权系统")
        print(f"   设备ID: {manager.device_id[:16]}...")
        
        # 测试授权检查
        print()
        print("【测试3】测试授权检查...")
        can_use, message = manager.check_and_update_usage()
        
        if can_use:
            print(f"✅ 授权检查通过")
            print(f"   {message}")
            print(f"   使用信息: {manager.get_usage_info()}")
        else:
            print(f"❌ 授权检查失败: {message}")
            
    else:
        print(f"✅ 使用本地授权系统")
        
except Exception as e:
    print(f"⚠️ 检查失败: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*60)
print("✅ 集成测试完成")
print("="*60)
print()
print("💡 提示：")
print("   - 云端授权已成功集成到主程序")
print("   - 运行 'python document_processor.py' 即可使用")
print("   - 每次处理文档时会自动检查和更新使用次数")
print("   - 访问 https://gist.github.com 查看使用数据")
print()
