#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云端授权快速配置工具
"""

import os
import sys


def main():
    print("=" * 60)
    print("云端授权系统快速配置")
    print("=" * 60)
    print()
    
    print("📌 步骤1：获取 GitHub Personal Access Token")
    print("   1. 访问：https://github.com/settings/tokens")
    print("   2. 点击 'Generate new token (classic)'")
    print("   3. 输入描述：Document Processor License")
    print("   4. 勾选权限：gist")
    print("   5. 点击 'Generate token'")
    print("   6. 复制生成的 token（ghp_ 开头）")
    print()
    
    token = input("请粘贴你的 GitHub Token: ").strip()
    
    if not token:
        print("❌ Token 不能为空")
        return
    
    if not token.startswith('ghp_'):
        print("⚠️ Token 格式可能不正确（应该以 ghp_ 开头）")
        confirm = input("是否继续？(y/n): ")
        if confirm.lower() != 'y':
            return
    
    print()
    print("📌 步骤2：配置选项")
    
    max_count = input(f"最大使用次数 [默认: 200]: ").strip()
    max_count = int(max_count) if max_count else 200
    
    timeout = input(f"网络超时（秒）[默认: 5]: ").strip()
    timeout = int(timeout) if timeout else 5
    
    print()
    print("📌 步骤3：生成配置文件")
    
    config_content = f'''# 云端授权配置文件
# 自动生成，请勿手动编辑（除非你知道你在做什么）

# GitHub Token
GITHUB_TOKEN = "{token}"

# 最大使用次数
MAX_USAGE_COUNT = {max_count}

# 网络超时时间（秒）
TIMEOUT = {timeout}

# 是否启用云端授权
USE_CLOUD = True
'''
    
    config_file = 'license_config.py'
    
    if os.path.exists(config_file):
        confirm = input(f"⚠️ {config_file} 已存在，是否覆盖？(y/n): ")
        if confirm.lower() != 'y':
            print("❌ 取消配置")
            return
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"✅ 配置文件已生成：{config_file}")
        print()
        
        # 测试配置
        print("📌 步骤4：测试配置")
        test = input("是否立即测试？(y/n): ")
        
        if test.lower() == 'y':
            print()
            print("开始测试...")
            print("-" * 60)
            
            try:
                from cloud_license import CloudLicenseManager
                
                manager = CloudLicenseManager()
                
                if not manager.GITHUB_TOKEN:
                    print("❌ Token 加载失败")
                    return
                
                print()
                print("测试云端连接...")
                can_use, message = manager.check_and_update_usage()
                
                print()
                print("-" * 60)
                if can_use:
                    print(f"✅✅✅ 测试成功！")
                    print(f"消息: {message}")
                    print(f"使用信息: {manager.get_usage_info()}")
                    print()
                    print("🎉 配置完成！现在可以使用云端授权了。")
                else:
                    print(f"❌ 测试失败: {message}")
                    
            except Exception as e:
                print(f"❌ 测试异常: {e}")
                import traceback
                traceback.print_exc()
        else:
            print()
            print("✅ 配置完成！")
            print()
            print("下一步：")
            print("  1. 运行 'python cloud_license.py' 测试")
            print("  2. 或直接使用主程序")
            
    except Exception as e:
        print(f"❌ 生成配置文件失败: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 60)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户取消")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
