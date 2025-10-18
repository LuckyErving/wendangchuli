# 📥 如何在GitHub Actions下载exe文件

## ❓ 为什么找不到exe文件？

### 可能的原因：

1. **✅ workflow正在运行中** - 还没构建完成
2. **❌ workflow构建失败** - 出现错误，没有生成文件
3. **🔍 不知道在哪里下载** - 位置不明显

---

## 📍 正确的下载位置

### 步骤1: 访问Actions页面

1. 打开你的GitHub仓库：`https://github.com/LuckyErving/wendangchuli`
2. 点击顶部的 **Actions** 标签（在Code、Issues、Pull requests旁边）

### 步骤2: 找到成功的workflow运行

在左侧栏：
- 点击 **Build Windows Executable**（workflow名称）

在右侧主区域，你会看到workflow运行历史列表：
- ✅ **绿色勾号** = 构建成功
- ❌ **红色X** = 构建失败
- 🔄 **黄色圈** = 正在运行

### 步骤3: 进入成功的构建

1. 点击一个**带绿色勾号**的workflow运行
2. 在打开的页面中，往下滚动到底部

### 步骤4: 下载Artifacts

在页面底部，你会看到一个 **Artifacts** 区域：

```
Artifacts
  文档处理器-Windows
  Uploaded 5 minutes ago · 15.2 MB
```

点击 `文档处理器-Windows` 即可下载！

---

## 🔍 排查问题

### 问题1: 所有workflow都是红色X（失败）

**解决方法**：
1. 点击失败的workflow
2. 查看错误日志
3. 根据错误信息修复问题
4. 重新推送代码触发构建

**最近的常见错误**：
- ✅ 已修复：actions版本过旧
- ✅ 已修复：Windows保留文件名nul
- ✅ 已修复：spec文件路径错误

### 问题2: workflow一直是黄色圈（运行中）

**原因**：构建需要时间（通常5-10分钟）

**解决方法**：
1. 等待完成
2. 可以点击进去查看实时日志

### 问题3: 没有Artifacts区域

**原因**：workflow构建失败或被取消

**检查**：
1. workflow状态必须是绿色勾号
2. 查看日志确认 "Upload artifact" 步骤成功执行

### 问题4: Artifacts过期了

**原因**：设置了30天保留期

**解决方法**：
1. 重新触发构建
2. 或修改 `retention-days` 设置

---

## 🎯 手动触发构建

如果想立即重新构建：

### 方法1: 通过GitHub网页

1. 进入 **Actions** 标签
2. 左侧选择 **Build Windows Executable**
3. 右上角点击 **Run workflow** 按钮
4. 选择 `main` 分支
5. 点击绿色的 **Run workflow** 按钮

### 方法2: 推送代码

```bash
# 创建空提交
git commit --allow-empty -m "trigger build"
git push
```

---

## 📊 查看当前构建状态

### 在终端查看最近的提交

```bash
git log --oneline -5
```

### 检查workflow配置

```bash
cat .github/workflows/build_windows.yml
```

---

## 🎨 可视化指南

### GitHub Actions页面结构

```
GitHub仓库页面
├── Code (代码)
├── Issues (问题)
├── Pull requests (PR)
├── ⭐ Actions (这里！)     <-- 点这里
│   ├── 左侧：workflow列表
│   │   └── Build Windows Executable
│   └── 右侧：运行历史
│       ├── ✅ 成功的运行  <-- 点进去
│       ├── ❌ 失败的运行
│       └── 🔄 运行中
└── Settings (设置)

点击成功的运行后：
└── 页面底部
    └── Artifacts 区域      <-- 在这里下载
        └── 文档处理器-Windows
            └── [点击下载 zip]
```

---

## 🔧 troubleshooting命令

### 检查本地文件是否已提交

```bash
git status
```

### 检查远程是否最新

```bash
git fetch
git log origin/main --oneline -5
```

### 强制触发构建

```bash
git commit --allow-empty -m "rebuild"
git push
```

---

## ✅ 验证构建成功

成功的构建日志应该显示：

```
✅ Checkout code
✅ Set up Python
✅ Install dependencies
✅ Build executable
✅ Upload artifact
```

如果所有步骤都是绿色勾号，就能在Artifacts区域下载exe文件了！

---

## 📞 如果还是找不到

1. **确认workflow已成功运行**
   - 访问：`https://github.com/LuckyErving/wendangchuli/actions`
   - 查看是否有绿色勾号的运行记录

2. **查看最新的workflow**
   - 点击最上面（最新）的运行记录
   - 滚动到页面底部
   - 查找 "Artifacts" 标题

3. **如果Artifacts区域为空**
   - 说明构建失败或上传失败
   - 查看日志中的错误信息

4. **检查保留期限**
   - 当前设置：30天
   - 超过30天的artifacts会自动删除

---

## 🎁 下载后的步骤

1. **解压zip文件**
   - 下载的是一个zip压缩包
   - 解压后得到 `DocumentProcessor.exe`

2. **运行程序**
   - 双击 `DocumentProcessor.exe`
   - 或复制到目标Windows电脑上运行

3. **如果被Windows阻止**
   - 右键 → 属性 → 解除锁定
   - 或点击"更多信息" → "仍要运行"

---

**创建时间**: 2025-10-18  
**仓库**: LuckyErving/wendangchuli  
**Workflow**: Build Windows Executable
