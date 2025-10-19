#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试保存和验证功能
"""

import os
import sys
import platform

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from document_processor import LicenseManager

def test_save_and_verify():
    """测试保存和立即验证"""
    print("\n" + "="*60)
    print("测试：保存数据并立即验证")
    print("="*60)
    
    manager = LicenseManager()
    
    # 测试1：首次保存
    print("\n【测试1】首次保存和验证")
    test_data = {
        'device': 'test_device_hash',
        'count': 1,
        'first_use': '2025-10-19T10:00:00',
        'last_use': '2025-10-19T10:00:00'
    }
    
    result = manager.save_usage_data(test_data)
    print(f"保存结果: {result}")
    
    # 验证
    loaded = manager.load_usage_data()
    if loaded:
        print(f"验证成功: count={loaded.get('count')}")
        assert loaded.get('count') == 1, "计数不匹配！"
    else:
        print("❌ 验证失败：无法加载数据")
        return False
    
    # 测试2：连续更新
    print("\n【测试2】连续更新 10 次")
    for i in range(2, 12):
        test_data['count'] = i
        result = manager.save_usage_data(test_data)
        
        if result:
            loaded = manager.load_usage_data()
            if loaded and loaded.get('count') == i:
                print(f"✅ 第 {i} 次更新成功")
            else:
                print(f"❌ 第 {i} 次验证失败: 期望={i}, 实际={loaded.get('count') if loaded else 'None'}")
                return False
        else:
            print(f"❌ 第 {i} 次保存失败")
            return False
    
    print("\n" + "="*60)
    print("✅✅✅ 所有测试通过！")
    print("="*60)
    return True

def test_real_usage_flow():
    """模拟真实使用流程"""
    print("\n" + "="*60)
    print("测试：模拟真实使用流程")
    print("="*60)
    
    manager = LicenseManager()
    
    # 清空现有数据
    if os.path.exists(manager.config_file):
        os.remove(manager.config_file)
        print("已清空现有配置")
    
    # 模拟10次文档处理
    for i in range(1, 11):
        print(f"\n--- 第 {i} 次处理文档 ---")
        can_use, message = manager.check_and_update_usage()
        
        if can_use:
            print(f"✅ {message}")
            
            # 验证计数是否正确
            loaded = manager.load_usage_data()
            if loaded:
                actual_count = loaded.get('count')
                print(f"验证: 期望count={i}, 实际count={actual_count}")
                
                if actual_count != i:
                    print(f"❌❌❌ 计数错误！期望 {i}，实际 {actual_count}")
                    return False
            else:
                print("❌ 无法加载配置验证")
                return False
        else:
            print(f"❌ 使用被拒绝: {message}")
            return False
    
    print("\n" + "="*60)
    print("✅✅✅ 真实流程测试通过！")
    print("="*60)
    return True

if __name__ == '__main__':
    print(f"运行平台: {platform.system()}")
    print(f"Python版本: {sys.version}")
    
    # 运行测试
    success1 = test_save_and_verify()
    success2 = test_real_usage_flow()
    
    if success1 and success2:
        print("\n🎉🎉🎉 全部测试通过！")
        sys.exit(0)
    else:
        print("\n❌❌❌ 测试失败！")
        sys.exit(1)
