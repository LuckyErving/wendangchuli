# GitHub Actions 环境变量配置指南

## ✅ 已完成配置

### 1. 代码支持
- ✅ `cloud_license.py` 支持从环境变量读取 Token
- ✅ `.github/workflows/build_windows.yml` 已配置环境变量
- ✅ `license_config.py` 已加入 `.gitignore`
- ✅ 代码已推送到 GitHub

### 2. 工作原理

```python
# cloud_license.py 中的逻辑
try:
    # 尝试从本地配置文件导入（本地开发）
    from license_config import GITHUB_TOKEN, MAX_USAGE_COUNT, TIMEOUT
    self.GITHUB_TOKEN = GITHUB_TOKEN
    self.MAX_USAGE_COUNT = MAX_USAGE_COUNT
    self.TIMEOUT = TIMEOUT
except ImportError:
    # 导入失败时从环境变量读取（GitHub Actions）
    self.GITHUB_TOKEN = os.environ.get('DOC_PROC_GITHUB_TOKEN', '')
    self.MAX_USAGE_COUNT = 20
    self.TIMEOUT = 5
```

```yaml
# .github/workflows/build_windows.yml 中的配置
jobs:
  build-windows:
    runs-on: windows-latest
    env:
      DOC_PROC_GITHUB_TOKEN: ${{ secrets.DOC_PROC_GITHUB_TOKEN }}
    steps:
      - name: Checkout code
        ...
      - name: Build with PyInstaller
        ...
```

## 📋 下一步：配置 GitHub Secret

### 步骤1：访问仓库设置

访问：
```
https://github.com/LuckyErving/wendangchuli/settings/secrets/actions
```

或者：
1. 打开你的 GitHub 仓库
2. 点击 **Settings**（设置）
3. 左侧菜单点击 **Secrets and variables** → **Actions**

### 步骤2：添加 Secret

1. 点击右上角绿色按钮 **"New repository secret"**

2. 填写表单：
   - **Name**: `DOC_PROC_GITHUB_TOKEN`（必须完全一致）
   - **Secret**: `你的GitHub Personal Access Token`（从 license_config.py 中复制）

3. 点击 **"Add secret"**

### 步骤3：验证配置

添加后你会看到：
```
Repository secrets
DOC_PROC_GITHUB_TOKEN     Updated now
```

## 🧪 测试 Actions

### 触发构建

**方式1：推送代码**
```bash
git commit --allow-empty -m "test: 触发 Actions 构建"
git push origin main
```

**方式2：手动触发**
1. 访问：https://github.com/LuckyErving/wendangchuli/actions
2. 选择 **"Build Windows Executable"** workflow
3. 点击 **"Run workflow"** → **"Run workflow"**

### 检查日志

1. 访问 Actions 页面
2. 点击最新的 workflow run
3. 查看 **"Build Windows Executable"** job
4. 检查日志中是否有：
   ```
   [云授权] 设备ID: ...
   [云授权] Gist ID: ...
   ```

如果没有报错，说明环境变量配置成功！

## 🔍 故障排查

### 问题1：Token 未生效

**症状**：
```
[云授权] ⚠️ 未配置 GitHub Token
```

**解决**：
1. 确认 Secret 名称是 `DOC_PROC_GITHUB_TOKEN`（大小写完全一致）
2. 重新运行 workflow

### 问题2：导入错误

**症状**：
```
ImportError: cannot import name 'GITHUB_TOKEN' from 'license_config'
```

**解决**：
这是正常的！`except ImportError` 会捕获这个错误，然后从环境变量读取。

### 问题3：Token 无效

**症状**：
```
[云授权] ❌ 创建 Gist 失败: 401
```

**解决**：
1. 检查 Token 是否正确
2. 检查 Token 是否有 `gist` 权限
3. 检查 Token 是否过期

## 📊 配置对比

| 环境 | Token 来源 | 配置文件 | 是否提交到 Git |
|------|-----------|---------|--------------|
| 本地开发 | `license_config.py` | 本地创建 | ❌ 不提交 |
| GitHub Actions | 环境变量 `DOC_PROC_GITHUB_TOKEN` | Secret | ✅ Secret 安全 |
| 用户 exe | 打包时内置 | - | - |

## ✅ 安全检查清单

- [x] `license_config.py` 已加入 `.gitignore`
- [x] 本地仍可正常开发（使用 `license_config.py`）
- [x] GitHub Actions 使用 Secret（不暴露 Token）
- [x] 代码已推送，不包含 Token
- [x] Workflow 文件已配置环境变量

## 🎉 总结

现在的配置：
- ✅ **本地开发**：使用 `license_config.py`（不提交）
- ✅ **GitHub Actions**：使用环境变量（从 Secret 读取）
- ✅ **安全性**：Token 不会暴露在代码中
- ✅ **易用性**：本地开发体验不变

**只需要在 GitHub 添加 Secret，就可以开始自动构建了！** 🚀

---

## 附录：本地配置文件示例

如果需要创建本地 `license_config.py`：

```python
# license_config.py（本地开发用，不要提交到 Git）

# GitHub Token
GITHUB_TOKEN = "ghp_你的token"

# 最大使用次数
MAX_USAGE_COUNT = 200

# 网络超时时间（秒）
TIMEOUT = 5

# 是否启用云端授权
USE_CLOUD = True
```

**记住：这个文件只在本地使用，永远不要提交到 Git！**
