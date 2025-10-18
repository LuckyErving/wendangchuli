# Windows保留文件名问题解决

## ❌ 问题
GitHub Actions在Windows上运行时报错：
```
error: invalid path 'nul'
```

## 🔍 原因
Windows系统有一些保留的设备名称，不能作为文件名：

### Windows保留名称列表
- `CON` - 控制台
- `PRN` - 打印机
- `AUX` - 辅助设备
- `NUL` - 空设备（相当于Unix的/dev/null）
- `COM1`-`COM9` - 串口
- `LPT1`-`LPT9` - 并口

这些名称**不能**在Windows上作为文件名或目录名使用（即使有扩展名也不行，如`nul.txt`）。

## ✅ 解决方案

### 1. 删除保留名称的文件
```bash
# 从Git仓库中删除
git rm nul
git rm "文档处理器_Windows一键打包版/nul"
git commit -m "fix: 删除Windows保留文件名nul"
git push
```

### 2. 避免创建这些文件
在macOS/Linux上开发时要小心：
- ❌ 不要创建名为 `nul`, `con`, `prn` 等的文件
- ❌ 不要使用 `> nul` 重定向（应该用 `/dev/null`）
- ✅ 使用跨平台兼容的文件名

### 3. 检查现有文件
```bash
# 检查Git仓库中是否有Windows保留名称
git ls-files | grep -iE "(^|/)((con|prn|aux|nul|com[0-9]|lpt[0-9])(\.|$))"
```

## 📝 如何产生这个文件的？

可能的原因：
1. **Shell重定向错误**：在macOS上误用了 `> nul`（应该是 `> /dev/null`）
2. **脚本兼容性问题**：Windows批处理脚本的 `> nul` 在macOS上创建了实际文件
3. **测试文件**：手动创建的测试文件

## 🛡️ 预防措施

### 在 .gitignore 中添加
```gitignore
# Windows保留设备名
nul
con
prn
aux
com[1-9]
lpt[1-9]
```

### 在脚本中使用跨平台写法
```bash
# ❌ 错误（Windows特定）
command > nul 2>&1

# ✅ 正确（跨平台）
command > /dev/null 2>&1

# ✅ 正确（Python）
import os
devnull = os.devnull  # 自动适配平台
```

## 📚 相关链接
- [Windows文件名命名约定](https://docs.microsoft.com/en-us/windows/win32/fileio/naming-a-file)
- [Git在Windows上的路径问题](https://github.com/git-for-windows/git/wiki/FAQ)

## ✨ 当前状态
✅ 已删除 `nul` 文件  
✅ 已提交并推送到GitHub  
✅ GitHub Actions应该能正常运行了

下次GitHub Actions运行时，Windows checkout应该能成功！
