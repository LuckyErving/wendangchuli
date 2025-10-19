#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重置 Gist 中的使用次数
"""

import requests
import json
from license_config import GITHUB_TOKEN

GIST_ID = "43dee181c2ae733f8040bc89d0efb00e"
GIST_API_URL = f"https://api.github.com/gists/{GIST_ID}"

print("=" * 60)
print("重置 Gist 使用次数")
print("=" * 60)

# 读取当前 Gist 内容
headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

response = requests.get(GIST_API_URL, headers=headers, timeout=10)
if response.status_code != 200:
    print(f"❌ 读取 Gist 失败: {response.status_code}")
    exit(1)

data = json.loads(response.json()['files']['licenses.json']['content'])
print(f"\n当前数据:")
print(json.dumps(data, indent=2))

# 获取设备ID
import hashlib
import uuid

def get_device_id():
    try:
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                       for elements in range(0, 48, 8)][::-1])
        salt = "doc_processor_cloud_v1"
        return hashlib.sha256(f"{mac}{salt}".encode()).hexdigest()
    except:
        return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()

device_id = get_device_id()
print(f"\n当前设备ID: {device_id[:16]}...")

# 重置 count
if device_id in data['devices']:
    old_count = data['devices'][device_id]['count']
    data['devices'][device_id]['count'] = 0
    print(f"\n重置 count: {old_count} → 0")
else:
    print(f"\n⚠️ 设备不存在，无需重置")
    exit(0)

# 保存到 Gist
payload = {
    "files": {
        "licenses.json": {
            "content": json.dumps(data, indent=2)
        }
    }
}

response = requests.patch(GIST_API_URL, headers=headers, json=payload, timeout=10)
if response.status_code == 200:
    print(f"✅ 重置成功！")
    print(f"\n新数据:")
    print(json.dumps(data, indent=2))
else:
    print(f"❌ 重置失败: {response.status_code}")
    print(response.text)

print("\n" + "=" * 60)
