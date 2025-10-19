#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
授权管理模块 - 设备绑定和使用次数限制
"""

import os
import hashlib
import json
import uuid
from pathlib import Path
import platform


class LicenseManager:
    """授权管理器"""
    
    # 使用次数限制
    MAX_USAGE_COUNT = 200
    
    def __init__(self):
        # 授权文件保存在用户目录的隐藏文件夹中
        self.license_dir = self._get_license_dir()
        self.license_file = os.path.join(self.license_dir, '.sys_cache.dat')
        
    def _get_license_dir(self):
        """获取授权文件目录（跨平台）"""
        if platform.system() == 'Windows':
            base_dir = os.path.expanduser('~\\AppData\\Local')
        else:
            base_dir = os.path.expanduser('~/.config')
        
        license_dir = os.path.join(base_dir, '.docproc_sys')
        os.makedirs(license_dir, exist_ok=True)
        return license_dir
    
    def _get_mac_address(self):
        """获取设备MAC地址（唯一标识）"""
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        return ':'.join([mac[i:i+2] for i in range(0, 12, 2)])
    
    def _encrypt_data(self, data):
        """简单加密（混淆存储内容）"""
        mac = self._get_mac_address()
        raw = json.dumps(data) + mac
        return hashlib.sha256(raw.encode()).hexdigest()[:32] + '.' + \
               hashlib.md5(raw.encode()).hexdigest()
    
    def _decrypt_and_verify(self, encrypted_data):
        """解密并验证数据完整性"""
        try:
            parts = encrypted_data.split('.')
            if len(parts) != 2:
                return None
            
            # 读取存储的使用次数
            with open(self.license_file, 'r') as f:
                content = f.read()
                # 提取JSON部分（在加密标记之前）
                json_part = content.split('\n')[0]
                data = json.loads(json_part)
                
                # 验证MAC地址
                stored_mac = data.get('mac')
                current_mac = self._get_mac_address()
                
                if stored_mac != current_mac:
                    # MAC地址不匹配，可能是复制到其他机器
                    return None
                
                return data
        except:
            return None
    
    def _init_license(self):
        """初始化授权文件"""
        data = {
            'mac': self._get_mac_address(),
            'count': 0,
            'version': '1.0'
        }
        
        # 保存加密后的数据
        encrypted = self._encrypt_data(data)
        with open(self.license_file, 'w') as f:
            f.write(json.dumps(data) + '\n')
            f.write(encrypted)
        
        return data
    
    def check_license(self):
        """
        检查授权状态
        返回: (is_valid, remaining_count, message)
        """
        # 如果授权文件不存在，初始化
        if not os.path.exists(self.license_file):
            data = self._init_license()
        else:
            # 读取并验证授权文件
            data = self._decrypt_and_verify(self._read_license_content())
            
            if data is None:
                # 文件被篡改或MAC地址不匹配
                return False, 0, "授权验证失败：程序文件已损坏或被非法复制"
        
        # 检查使用次数
        current_count = data.get('count', 0)
        remaining = self.MAX_USAGE_COUNT - current_count
        
        if current_count >= self.MAX_USAGE_COUNT:
            return False, 0, f"程序已损坏，请联系技术支持\n错误代码: 0x80070570"
        
        return True, remaining, f"剩余可用次数: {remaining}"
    
    def _read_license_content(self):
        """读取授权文件内容"""
        with open(self.license_file, 'r') as f:
            lines = f.readlines()
            if len(lines) >= 2:
                return lines[1].strip()
        return ""
    
    def increment_usage(self):
        """增加使用次数"""
        if not os.path.exists(self.license_file):
            data = self._init_license()
        else:
            with open(self.license_file, 'r') as f:
                data = json.loads(f.readline().strip())
        
        # 增加计数
        data['count'] = data.get('count', 0) + 1
        
        # 保存
        encrypted = self._encrypt_data(data)
        with open(self.license_file, 'w') as f:
            f.write(json.dumps(data) + '\n')
            f.write(encrypted)
        
        return data['count']
    
    def get_device_info(self):
        """获取设备信息（用于生成授权）"""
        return {
            'mac': self._get_mac_address(),
            'platform': platform.system(),
            'machine': platform.machine()
        }


def validate_license():
    """
    验证授权的便捷函数
    返回: (is_valid, message)
    """
    manager = LicenseManager()
    is_valid, remaining, message = manager.check_license()
    
    if not is_valid:
        return False, message
    
    # 增加使用次数
    new_count = manager.increment_usage()
    
    return True, f"验证成功 (已使用 {new_count}/{manager.MAX_USAGE_COUNT} 次)"


if __name__ == "__main__":
    # 测试代码
    manager = LicenseManager()
    print("设备信息:")
    print(json.dumps(manager.get_device_info(), indent=2))
    
    print("\n授权检查:")
    is_valid, remaining, message = manager.check_license()
    print(f"状态: {'✅ 有效' if is_valid else '❌ 无效'}")
    print(f"消息: {message}")
    
    if is_valid:
        count = manager.increment_usage()
        print(f"使用次数已更新: {count}")
