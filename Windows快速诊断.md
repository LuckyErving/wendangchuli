# Windows次数问题 - 快速解决方案

## 🔍 问题：Windows上exe使用次数不减少

### 快速诊断 3 步骤

1. **打包DEBUG版本**（能看到日志）
   ```batch
   pyinstaller --clean --onefile --console --name DocumentProcessor_Debug document_processor.py
   ```

2. **运行并保存日志**
   ```batch
   DocumentProcessor_Debug.exe > log.txt 2>&1
   ```
   - 选择文件夹
   - 处理2-3次文档
   - 关闭程序

3. **查看日志文件**
   ```batch
   type log.txt
   ```

## 📋 日志应该显示什么

### ✅ 正常情况
```
[授权] 配置目录: C:\Users\xxx\AppData\Roaming\.docproc
[授权] 配置目录创建成功
[授权] 配置文件: C:\Users\xxx\AppData\Roaming\.docproc\.lic
[授权] ========== 开始检查并更新使用次数 ==========
[授权] MAC地址: xx:xx:xx:xx:xx:xx
[授权] 设备哈希: abbb34271fd11eb9...
[授权] 配置加载成功，已使用 1 次
[授权] 当前使用次数: 1/200
[授权] 更新使用次数: 1 → 2
[授权] 准备保存: count=2
[授权] ✅ 保存成功: C:\Users\xxx\AppData\Roaming\.docproc\.lic
[授权] ✅ 检查通过，剩余次数: 198
```

### ❌ 异常情况

**问题1: 配置目录创建失败**
```
[授权] ⚠️ 创建配置目录失败: [WinError 5] 拒绝访问
```
**解决**: 以管理员身份运行

**问题2: 配置文件保存失败**
```
[授权] ❌ 保存使用记录失败: [Errno 13] Permission denied
```
**解决**: 
- 检查杀毒软件
- 添加到白名单
- 关闭勒索软件保护

**问题3: 配置不存在（每次）**
```
[授权] 配置文件不存在，首次使用
[授权] 配置文件不存在，首次使用  # ← 重复出现
```
**解决**: 保存失败，查看后续错误信息

## 🛠️ 快速修复

### 修复1: 管理员权限
右键exe → 以管理员身份运行

### 修复2: 检查配置文件
```batch
# 检查是否存在
dir %APPDATA%\.docproc

# 如果不存在，手动创建
mkdir %APPDATA%\.docproc

# 再次运行程序
```

### 修复3: 杀毒软件白名单
- 打开Windows Defender安全中心
- 病毒和威胁防护
- 管理勒索软件保护
- 允许应用通过受控文件夹访问
- 添加exe路径

### 修复4: 查看实际配置路径
在cmd中运行：
```batch
echo %APPDATA%
dir %APPDATA%\.docproc
type %APPDATA%\.docproc\.lic
```

## 📊 测试验证

### 测试1: 计数功能
```
1. 运行exe，处理1个文档 → 显示"剩余199次"
2. 再处理1个文档 → 显示"剩余198次"
3. 关闭程序
4. 重新打开 → 应该显示"已使用: 2次，剩余198次"
```

### 测试2: 配置持久化
```batch
# 第1次运行
DocumentProcessor_Debug.exe
# 处理2个文档后关闭

# 检查配置文件
type %APPDATA%\.docproc\.lic
# 应该看到加密的内容

# 第2次运行
DocumentProcessor_Debug.exe
# 应该显示"已使用: 2次"（不是0次）
```

## 📞 还是不行？发送这些信息

1. **log.txt 完整内容**
2. **配置文件检查结果**
   ```batch
   dir %APPDATA%\.docproc
   ```
3. **Windows版本**
   ```batch
   ver
   ```
4. **用户权限**
   ```batch
   whoami /groups | find "Administrators"
   ```

## 🎯 最可能的原因

根据经验，90%是以下之一：
1. **权限不足** → 以管理员身份运行
2. **杀毒软件阻止** → 添加白名单
3. **路径问题** → 检查%APPDATA%环境变量

---

**最新代码已包含完整日志，运行debug版本即可找到问题！** 🔧
