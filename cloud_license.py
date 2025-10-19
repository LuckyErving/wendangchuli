#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云端授权管理系统
使用 GitHub Gist 作为免费云端存储
"""

import os
import sys
import json
import hashlib
import uuid
import platform
import requests
from datetime import datetime
from typing import Tuple, Optional


class CloudLicenseManager:
    """云端授权管理器"""
    
    def __init__(self):
        # 从配置文件加载设置
        try:
            from license_config import GITHUB_TOKEN, MAX_USAGE_COUNT, TIMEOUT
            self.GITHUB_TOKEN = GITHUB_TOKEN
            self.MAX_USAGE_COUNT = MAX_USAGE_COUNT
            self.TIMEOUT = TIMEOUT
        except ImportError:
            # 如果没有配置文件，使用默认值
            self.GITHUB_TOKEN = os.environ.get('DOC_PROC_GITHUB_TOKEN', '')
            self.MAX_USAGE_COUNT = 20
            self.TIMEOUT = 5
        
        self.GIST_ID = None
        self.GIST_API_URL = "https://api.github.com/gists"
        
        self.device_id = self._get_device_id()
        self.cache_file = self._get_cache_file()
        
        # 尝试加载 Gist ID
        self._load_gist_config()
        
        print(f"[云授权] 设备ID: {self.device_id[:16]}...")
        print(f"[云授权] 缓存文件: {self.cache_file}")
        if self.GIST_ID:
            print(f"[云授权] Gist ID: {self.GIST_ID}")
        if not self.GITHUB_TOKEN:
            print(f"[云授权] ⚠️ 未配置 GitHub Token，请编辑 license_config.py")
    
    def _get_device_id(self) -> str:
        """获取唯一设备ID"""
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                           for elements in range(0, 48, 8)][::-1])
            salt = "doc_processor_cloud_v1"
            return hashlib.sha256(f"{mac}{salt}".encode()).hexdigest()
        except:
            return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
    
    def _get_cache_file(self) -> str:
        """获取本地缓存文件路径"""
        if platform.system() == 'Windows':
            appdata = os.environ.get('LOCALAPPDATA') or os.environ.get('APPDATA') or os.path.expanduser('~')
            cache_dir = os.path.join(appdata, '.docproc_cache')
        else:
            cache_dir = os.path.join(os.path.expanduser('~'), '.docproc_cache')
        
        os.makedirs(cache_dir, exist_ok=True)
        return os.path.join(cache_dir, '.license_cache')
    
    def _load_gist_config(self):
        """加载 Gist 配置"""
        config_file = os.path.join(os.path.dirname(__file__), '.gist_config')
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    self.GIST_ID = config.get('gist_id')
                    if config.get('github_token'):
                        self.GITHUB_TOKEN = config.get('github_token')
            except:
                pass
    
    def _save_gist_config(self, gist_id: str):
        """保存 Gist 配置"""
        config_file = os.path.join(os.path.dirname(__file__), '.gist_config')
        try:
            with open(config_file, 'w') as f:
                json.dump({'gist_id': gist_id, 'github_token': self.GITHUB_TOKEN}, f)
            self.GIST_ID = gist_id
        except Exception as e:
            print(f"[云授权] ⚠️ 保存配置失败: {e}")
    
    def _create_gist(self, data: dict) -> Optional[str]:
        """创建新的 Gist"""
        try:
            headers = {
                'Authorization': f'token {self.GITHUB_TOKEN}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            payload = {
                "description": "Document Processor License Data",
                "public": False,  # 私有 Gist
                "files": {
                    "licenses.json": {
                        "content": json.dumps(data, indent=2)
                    }
                }
            }
            
            response = requests.post(
                self.GIST_API_URL,
                headers=headers,
                json=payload,
                timeout=self.TIMEOUT
            )
            
            if response.status_code == 201:
                gist_id = response.json()['id']
                print(f"[云授权] ✅ 创建 Gist 成功: {gist_id}")
                self._save_gist_config(gist_id)
                return gist_id
            else:
                print(f"[云授权] ❌ 创建 Gist 失败: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[云授权] ❌ 创建 Gist 异常: {e}")
            return None
    
    def _load_from_cloud(self) -> Optional[dict]:
        """从云端加载数据"""
        if not self.GIST_ID:
            print(f"[云授权] Gist ID 未配置")
            return None
        
        try:
            headers = {
                'Authorization': f'token {self.GITHUB_TOKEN}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get(
                f"{self.GIST_API_URL}/{self.GIST_ID}",
                headers=headers,
                timeout=self.TIMEOUT
            )
            
            if response.status_code == 200:
                files = response.json()['files']
                content = files['licenses.json']['content']
                data = json.loads(content)
                print(f"[云授权] ✅ 从云端加载成功")
                return data
            else:
                print(f"[云授权] ⚠️ 从云端加载失败: {response.status_code}")
                return None
                
        except requests.Timeout:
            print(f"[云授权] ⚠️ 网络超时")
            return None
        except Exception as e:
            print(f"[云授权] ⚠️ 从云端加载异常: {e}")
            return None
    
    def _save_to_cloud(self, data: dict) -> bool:
        """保存数据到云端"""
        try:
            # 如果没有 Gist ID，先创建
            if not self.GIST_ID:
                gist_id = self._create_gist(data)
                if not gist_id:
                    return False
            
            headers = {
                'Authorization': f'token {self.GITHUB_TOKEN}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            payload = {
                "files": {
                    "licenses.json": {
                        "content": json.dumps(data, indent=2)
                    }
                }
            }
            
            response = requests.patch(
                f"{self.GIST_API_URL}/{self.GIST_ID}",
                headers=headers,
                json=payload,
                timeout=self.TIMEOUT
            )
            
            if response.status_code == 200:
                print(f"[云授权] ✅ 保存到云端成功")
                return True
            else:
                print(f"[云授权] ❌ 保存到云端失败: {response.status_code}")
                return False
                
        except requests.Timeout:
            print(f"[云授权] ⚠️ 网络超时")
            return False
        except Exception as e:
            print(f"[云授权] ❌ 保存到云端异常: {e}")
            return False
    
    def _load_from_cache(self) -> Optional[dict]:
        """从本地缓存加载"""
        if not os.path.exists(self.cache_file):
            return None
        
        try:
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
            print(f"[云授权] ✅ 从缓存加载成功")
            return data
        except Exception as e:
            print(f"[云授权] ⚠️ 从缓存加载失败: {e}")
            return None
    
    def _save_to_cache(self, data: dict) -> bool:
        """保存到本地缓存"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"[云授权] ✅ 保存到缓存成功")
            return True
        except Exception as e:
            print(f"[云授权] ❌ 保存到缓存失败: {e}")
            return False
    
    def _get_device_data(self, all_data: dict) -> Optional[dict]:
        """从所有数据中获取当前设备的数据"""
        devices = all_data.get('devices', {})
        return devices.get(self.device_id)
    
    def _update_device_data(self, all_data: dict, device_data: dict) -> dict:
        """更新当前设备的数据"""
        if 'devices' not in all_data:
            all_data['devices'] = {}
        all_data['devices'][self.device_id] = device_data
        all_data['last_update'] = datetime.now().isoformat()
        return all_data
    
    def check_and_update_usage(self) -> Tuple[bool, str]:
        """
        检查并更新使用次数（云端优先，缓存备份）
        返回: (是否允许使用, 消息)
        """
        print(f"\n[云授权] ========== 开始检查授权 ==========")
        
        # 1. 尝试从云端加载
        all_data = self._load_from_cloud()
        
        # 2. 如果云端失败，从缓存加载
        if all_data is None:
            print(f"[云授权] 云端不可用，使用缓存")
            all_data = self._load_from_cache()
        
        # 3. 如果都没有，初始化
        if all_data is None:
            print(f"[云授权] 首次使用，初始化数据")
            all_data = {
                'version': '1.0',
                'created_at': datetime.now().isoformat(),
                'devices': {}
            }
        
        # 4. 获取当前设备数据
        device_data = self._get_device_data(all_data)
        
        if device_data is None:
            # 新设备
            device_data = {
                'device_id': self.device_id,
                'count': 0,
                'first_use': datetime.now().isoformat(),
                'last_use': datetime.now().isoformat(),
                'platform': platform.system()
            }
            print(f"[云授权] 新设备注册")
        
        # 5. 检查使用次数
        current_count = device_data.get('count', 0)
        print(f"[云授权] 当前使用次数: {current_count}/{self.MAX_USAGE_COUNT}")
        
        if current_count >= self.MAX_USAGE_COUNT:
            print(f"[云授权] ❌ 已达到使用上限")
            return False, "程序已损坏"
        
        # 6. 更新使用次数
        device_data['count'] = current_count + 1
        device_data['last_use'] = datetime.now().isoformat()
        
        # 7. 更新数据
        all_data = self._update_device_data(all_data, device_data)
        
        # 8. 保存到云端（优先）
        cloud_saved = self._save_to_cloud(all_data)
        
        # 9. 保存到缓存（备份）
        cache_saved = self._save_to_cache(all_data)
        
        if not cloud_saved and not cache_saved:
            print(f"[云授权] ⚠️⚠️ 保存失败，但允许本次使用")
        
        remaining = self.MAX_USAGE_COUNT - device_data['count']
        print(f"[云授权] ✅ 检查通过，剩余次数: {remaining}")
        print(f"[云授权] ========== 检查完成 ==========\n")
        
        return True, "验证通过"
    
    def get_usage_info(self) -> str:
        """获取使用信息（不显示具体次数）"""
        return "正常"


# 测试代码
if __name__ == '__main__':
    print("云端授权系统测试")
    print("=" * 60)
    
    manager = CloudLicenseManager()
    
    # 测试授权检查
    can_use, message = manager.check_and_update_usage()
    print(f"\n结果: {can_use}")
    print(f"消息: {message}")
    print(f"使用信息: {manager.get_usage_info()}")
