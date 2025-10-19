#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整测试：从正常使用到达到限制
"""

import requests
import json
from license_config import GITHUB_TOKEN

GIST_ID = "43dee181c2ae733f8040bc89d0efb00e"
GIST_API_URL = f"https://api.github.com/gists/{GIST_ID}"

def get_device_id():
    import hashlib
    import uuid
    try:
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                       for elements in range(0, 48, 8)][::-1])
        salt = "doc_processor_cloud_v1"
        return hashlib.sha256(f"{mac}{salt}".encode()).hexdigest()
    except:
        return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()

def set_count(count):
    """设置 Gist 中的 count"""
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    response = requests.get(GIST_API_URL, headers=headers, timeout=10)
    if response.status_code != 200:
        print(f"❌ 读取 Gist 失败: {response.status_code}")
        return False
    
    data = json.loads(response.json()['files']['licenses.json']['content'])
    device_id = get_device_id()
    
    if device_id in data['devices']:
        data['devices'][device_id]['count'] = count
    else:
        print(f"❌ 设备不存在")
        return False
    
    payload = {
        "files": {
            "licenses.json": {
                "content": json.dumps(data, indent=2)
            }
        }
    }
    
    response = requests.patch(GIST_API_URL, headers=headers, json=payload, timeout=10)
    return response.status_code == 200

def test_authorization():
    """测试授权"""
    from cloud_license import CloudLicenseManager
    manager = CloudLicenseManager()
    can_use, message = manager.check_and_update_usage()
    return can_use, message

print("=" * 60)
print("完整授权测试")
print("=" * 60)

# 测试1: count = 198 (未达到限制)
print("\n测试1: count = 198 (应该允许)")
print("-" * 60)
if set_count(198):
    can_use, msg = test_authorization()
    print(f"结果: {'✅ 允许' if can_use else '❌ 拒绝'}")
    print(f"消息: {msg}")
    if can_use:
        print("✅ 正确：允许使用，count应该变为199")
    else:
        print("❌ 错误：应该允许但拒绝了")

# 测试2: count = 199 (最后一次)
print("\n测试2: count = 199 (最后一次，应该允许)")
print("-" * 60)
if set_count(199):
    can_use, msg = test_authorization()
    print(f"结果: {'✅ 允许' if can_use else '❌ 拒绝'}")
    print(f"消息: {msg}")
    if can_use:
        print("✅ 正确：允许最后一次使用，count应该变为200")
    else:
        print("❌ 错误：应该允许但拒绝了")

# 测试3: count = 200 (已达到限制)
print("\n测试3: count = 200 (已达到限制，应该拒绝)")
print("-" * 60)
if set_count(200):
    can_use, msg = test_authorization()
    print(f"结果: {'✅ 拒绝' if not can_use else '❌ 允许'}")
    print(f"消息: {msg}")
    if not can_use and msg == "程序已损坏":
        print("✅ 正确：拒绝使用，显示'程序已损坏'")
    else:
        print("❌ 错误：应该拒绝但允许了，或消息不正确")

# 测试4: count = 201 (超过限制)
print("\n测试4: count = 201 (超过限制，应该拒绝)")
print("-" * 60)
if set_count(201):
    can_use, msg = test_authorization()
    print(f"结果: {'✅ 拒绝' if not can_use else '❌ 允许'}")
    print(f"消息: {msg}")
    if not can_use and msg == "程序已损坏":
        print("✅ 正确：拒绝使用，显示'程序已损坏'")
    else:
        print("❌ 错误：应该拒绝但允许了，或消息不正确")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
