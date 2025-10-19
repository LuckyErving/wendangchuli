# 📘 Windows用户使用指南

## ✅ Windows系统要求

### 必需软件

#### 1. **Microsoft Word**（必需！）
程序在Windows上转换Word文档(.docx)为PDF需要依赖Microsoft Word。

**为什么需要Word？**
- Windows版本使用 `docx2pdf` Python库
- `docx2pdf` 通过COM接口调用系统安装的Word进行转换
- 没有Word就无法转换.docx文件

**支持的Word版本：**
- ✅ Microsoft Office 2010
- ✅ Microsoft Office 2013
- ✅ Microsoft Office 2016
- ✅ Microsoft Office 2019
- ✅ Microsoft Office 2021
- ✅ Microsoft 365 (Office 365)

**不支持的替代品：**
- ❌ WPS Office - 不支持
- ❌ LibreOffice - 不支持（COM接口不兼容）
- ❌ 在线Office - 不支持

---

## 🚀 快速开始

### 步骤1: 检查是否已安装Word

1. 点击Windows开始菜单
2. 搜索 "Word" 或 "Microsoft Word"
3. 如果能找到并打开，说明已安装 ✅

### 步骤2: 运行程序

1. 下载 `DocumentProcessor.exe`
2. 双击运行
3. 选择包含文档的文件夹
4. 点击"开始处理并保存"

### 步骤3: 查看结果

程序会自动：
- ✅ 识别所有文档类型
- ✅ 转换Word文档为PDF（使用Word）
- ✅ 转换图片为PDF
- ✅ 按顺序合并所有PDF

---

## ❌ 如果没有安装Word

### 情况说明

如果Windows电脑上**没有安装Microsoft Word**：

**会发生什么：**
1. 程序会尝试转换.docx文件
2. 转换会失败
3. 显示错误："请确保已安装Microsoft Word"
4. ⚠️ **该Word文档不会包含在最终PDF中**
5. 其他文件（PDF、图片）仍会正常处理

**程序日志会显示：**
```
正在处理: 承诺书-发证签订.docx
  [Windows] 使用docx2pdf转换Word文档...
  ✗ Word转PDF失败: ...
  提示: 请确保已安装Microsoft Word，docx2pdf需要Word才能工作
```

---

## 💡 解决方案

### 方案1: 安装Microsoft Word（推荐）

**购买途径：**
1. **Microsoft 365订阅**（推荐）
   - 价格：约￥398/年（个人版）
   - 包含Word、Excel、PowerPoint等
   - 总是最新版本
   - 官网：https://www.microsoft.com/zh-cn/microsoft-365

2. **Office 2021永久许可**
   - 价格：约￥748（一次性购买）
   - 不包含更新
   - 官网购买

3. **学校/公司许可**
   - 很多学校和公司提供免费Office
   - 询问你的IT部门

**安装后：**
1. 重启程序
2. 程序会自动检测Word
3. 可以正常转换.docx文件

---

### 方案2: 手动转换Word文档

如果暂时无法安装Word：

#### 步骤：
1. **在Word中打开.docx文件**（其他电脑）
2. **文件 → 另存为 → PDF格式**
3. **将PDF文件放回文档文件夹**
4. **重命名保持关键字**（如"承诺书.pdf"）
5. **运行程序**

**注意**：文件名必须包含关键字（如"承诺书"）

---

### 方案3: 使用在线转换工具

**在线Word转PDF网站：**
- https://www.ilovepdf.com/zh-cn/word_to_pdf
- https://smallpdf.com/cn/word-to-pdf
- https://www.adobe.com/cn/acrobat/online/word-to-pdf.html

#### 步骤：
1. 上传.docx文件到网站
2. 下载转换后的PDF
3. 放回文档文件夹
4. 保持文件名包含关键字

---

### 方案4: 修改程序跳过Word文档

如果确定不需要Word文档：

**临时解决方案：**
将.docx文件移到其他文件夹，程序会忽略它。

---

## 🔍 常见问题

### Q1: 我安装了WPS Office，可以用吗？
**A:** ❌ 不可以。程序需要Microsoft Word的COM接口，WPS不兼容。

### Q2: 我有Office 2007，可以用吗？
**A:** ⚠️ 可能不行。建议使用Office 2010或更新版本。

### Q3: 我安装了Word，但还是转换失败？
**A:** 可能的原因：
1. Word没有激活
2. Word进程被占用（关闭所有Word窗口）
3. Word版本太旧
4. 文件损坏或有密码保护

**解决方法：**
1. 激活Word
2. 关闭所有Word程序
3. 更新到最新版本
4. 移除文档保护

### Q4: 转换很慢怎么办？
**A:** Word转换需要启动Word进程，首次转换较慢（10-30秒）是正常的。

### Q5: 能不能用LibreOffice替代Word？
**A:** ❌ Windows版本不支持。如果想用LibreOffice，需要在macOS或Linux上运行程序。

---

## 📊 文档类型支持情况

| 文件类型 | Windows支持 | 依赖软件 |
|---------|------------|----------|
| PDF | ✅ 完全支持 | 无 |
| JPG/PNG | ✅ 完全支持 | 无 |
| DOCX | ⚠️ 需要Word | Microsoft Word |
| DOC | ⚠️ 需要Word | Microsoft Word |

---

## 🎯 最佳实践

### 建议做法：

1. **统一使用PDF格式**
   - 在Word中另存为PDF
   - 避免依赖转换功能

2. **检查Word安装**
   - 运行前确认Word已安装且激活
   - 关闭所有Word窗口

3. **备份原始文件**
   - 处理前备份所有文档
   - 防止意外丢失

4. **测试小批量**
   - 先用少量文件测试
   - 确认无误后批量处理

---

## 🔄 程序工作流程

```
选择文件夹
    ↓
扫描所有文件
    ↓
识别文档类型（承诺书、申请书等）
    ↓
转换为PDF
    ├── PDF文件 → 直接复制
    ├── 图片文件 → 转换为PDF
    └── Word文档 → 调用Word转换 ⚠️ 需要Word
    ↓
按规定顺序排列
    ↓
合并为一个PDF
    ↓
保存输出文件
```

---

## 📞 获取帮助

### 如果遇到问题：

1. **查看程序窗口的日志**
   - 显示详细的处理过程
   - 包含错误信息

2. **检查以下内容：**
   - [ ] Word是否已安装
   - [ ] Word是否已激活
   - [ ] Word窗口是否已关闭
   - [ ] 文件名是否包含关键字
   - [ ] 文件是否有密码保护

3. **如果Word未安装：**
   - 使用方案2或方案3手动转换
   - 或考虑购买/获取Word许可

---

## 📝 总结

### ✅ 有Word的情况
- 完全自动化
- 所有文档类型都支持
- 包括Word文档转换

### ⚠️ 没有Word的情况
- PDF和图片正常处理
- Word文档会跳过
- 需要手动转换Word为PDF

### 💡 建议
**如果经常需要处理Word文档，强烈建议安装Microsoft Word！**

---

**创建时间**: 2025-10-19  
**适用平台**: Windows 7 SP1 / Windows 10 / Windows 11  
**程序版本**: DocumentProcessor.exe
