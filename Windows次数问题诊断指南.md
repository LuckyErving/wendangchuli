# Windows打包exe次数不减少 - 诊断和修复指南

## 问题描述

在Windows上运行打包的exe文件，使用次数不会减少。

## 可能的原因

1. **权限问题**: exe无法写入配置文件到APPDATA目录
2. **路径问题**: 打包后获取APPDATA路径失败
3. **异常被忽略**: 错误被捕获但没有显示

## 修复内容

### 1. 增强路径处理
```python
if platform.system() == 'Windows':
    appdata = os.environ.get('APPDATA', '')
    if not appdata:
        # 备用方案：使用用户目录
        appdata = os.path.expanduser('~')
    self.config_dir = os.path.join(appdata, '.docproc')
```

### 2. 添加详细日志
所有关键操作都会输出日志：
```
[授权] 配置目录: C:\Users\xxx\AppData\Roaming\.docproc
[授权] 配置目录创建成功
[授权] 配置文件: C:\Users\xxx\AppData\Roaming\.docproc\.lic
[授权] ========== 开始检查并更新使用次数 ==========
[授权] MAC地址: xx:xx:xx:xx:xx:xx
[授权] 当前使用次数: 1/200
[授权] 更新使用次数: 1 → 2
[授权] 准备保存: count=2
[授权] ✅ 保存成功
[授权] ✅ 检查通过，剩余次数: 198
```

### 3. 完整的错误处理
```python
try:
    # 操作
except Exception as e:
    print(f"[授权] ❌ 错误: {e}")
    traceback.print_exc()
```

## 诊断步骤

### 方法1：使用诊断脚本

在包含exe的目录下运行：
```batch
test_windows.bat
```

这会检查：
- Python环境
- APPDATA目录
- 配置目录是否存在
- 配置文件是否创建
- 文件内容

### 方法2：手动检查

1. **检查配置目录**
   ```
   打开: %APPDATA%\.docproc
   应该看到: .lic 文件
   ```

2. **查看exe运行日志**
   - 以管理员身份运行cmd
   - 在exe所在目录运行: `DocumentProcessor.exe > log.txt 2>&1`
   - 查看 `log.txt` 文件中的日志

3. **检查文件权限**
   - 右键点击 `%APPDATA%` 目录
   - 属性 → 安全
   - 确保当前用户有"写入"权限

## 常见问题和解决方案

### 问题1: 配置文件不存在

**症状**: 使用次数始终是200
**原因**: 配置文件没有创建成功
**解决**:
1. 手动创建目录: `mkdir %APPDATA%\.docproc`
2. 确保有写入权限
3. 查看日志中的错误信息

### 问题2: 配置文件无法写入

**症状**: 日志显示"保存失败"
**原因**: 权限不足或路径错误
**解决**:
1. 以管理员身份运行exe
2. 检查杀毒软件是否阻止
3. 关闭文件保护功能

### 问题3: APPDATA环境变量不存在

**症状**: 配置目录路径错误
**原因**: 系统环境变量异常
**解决**:
```batch
# 检查环境变量
echo %APPDATA%

# 如果为空，手动设置
set APPDATA=%USERPROFILE%\AppData\Roaming
```

### 问题4: exe被阻止访问文件系统

**症状**: 没有任何错误，但文件不创建
**原因**: Windows安全策略或杀毒软件
**解决**:
1. 添加exe到杀毒软件白名单
2. 在Windows Defender中允许该应用
3. 关闭勒索软件保护（临时）

## 测试验证

### 测试脚本
```python
# test_simple.py
python test_simple.py
```

预期输出：
```
[授权] 配置目录: C:\Users\xxx\AppData\Roaming\.docproc
[授权] 配置目录创建成功
...
第 1 次处理文档:
  ✅ 允许处理
  状态: 已使用: 1 次，剩余: 199 次
```

### 检查配置文件
```batch
type %APPDATA%\.docproc\.lic
```

应该看到加密的内容（Base64编码的乱码）。

## 打包注意事项

### PyInstaller命令
```batch
pyinstaller --clean --onefile --windowed ^
  --name DocumentProcessor ^
  --hidden-import=PIL._tkinter_finder ^
  --hidden-import=tkinter ^
  ... (其他参数) ^
  document_processor.py
```

### 确保事项
1. ✅ 不要使用 `--onedir` (使用 `--onefile`)
2. ✅ 不要使用 `--noconsole` 调试时
3. ✅ 包含所有依赖库
4. ✅ 测试时保留console输出

### 调试版本打包
调试时使用console模式：
```batch
pyinstaller --clean --onefile ^
  --console ^
  --name DocumentProcessor_Debug ^
  document_processor.py
```

这样可以看到所有日志输出。

## 发布版本建议

### 步骤1: 调试版本
```batch
# 打包console版本
pyinstaller --clean --onefile --console document_processor.py

# 测试
DocumentProcessor_Debug.exe > debug_log.txt 2>&1

# 检查日志
type debug_log.txt
```

### 步骤2: 确认功能正常
- 运行3次
- 检查配置文件
- 确认次数递减
- 关闭重启，确认累计

### 步骤3: 打包发布版本
```batch
# 打包windowed版本（无console）
pyinstaller --clean --onefile --windowed document_processor.py
```

## 用户端问题排查

如果用户报告次数不减少：

1. **收集信息**
   ```
   - Windows版本
   - 用户账户类型（管理员/普通用户）
   - 杀毒软件
   - 是否有错误提示
   ```

2. **要求用户测试**
   ```batch
   # 检查配置目录
   dir %APPDATA%\.docproc
   
   # 检查配置文件
   dir %APPDATA%\.docproc\.lic
   ```

3. **临时解决方案**
   - 以管理员身份运行
   - 添加到杀毒软件白名单
   - 关闭Windows Defender实时保护（临时）

## 最终确认清单

打包发布前检查：

- [ ] 代码中有完整的日志输出
- [ ] 异常处理不会吞掉错误
- [ ] 路径处理有备用方案
- [ ] 配置目录创建有重试机制
- [ ] 本地测试console版本正常
- [ ] 本地测试windowed版本正常
- [ ] 在不同用户账户测试
- [ ] 关闭重启后测试累计
- [ ] 达到200次测试阻止

---

**修复已提交**: 增加了详细日志和错误处理，现在可以清楚看到问题所在。
