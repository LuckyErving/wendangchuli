# Token 安全处理指南

## ⚠️ 常见问题

### 问题：GitHub Push Protection 拦截

**症状**：
```
remote: error: GH013: Repository rule violations found for refs/heads/main.
remote: - GITHUB PUSH PROTECTION
remote:   - Push cannot contain secrets
remote:   - GitHub Personal Access Token
```

## ✅ 解决方案

### 步骤1：从文件中移除 Token

**不要直接写真实的 Token！**

❌ **错误示例**：
```markdown
- **Secret**: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`（真实 Token）
```

✅ **正确示例**：
```markdown
- **Secret**: `你的GitHub Personal Access Token`（从 license_config.py 中复制）
```

### 步骤2：清除 Git 历史中的 Token

如果已经提交了包含 Token 的文件：

```bash
# 1. 查看最近的提交
git log --oneline -5

# 2. 软重置到包含 Token 的提交之前
# 例如：删除最近 2 个提交
git reset --soft HEAD~2

# 3. 修改文件，移除 Token

# 4. 重新提交
git add -A
git commit -m "🔐 修复敏感信息泄露"

# 5. 强制推送（如果已经推送到远程）
git push origin main
```

### 步骤3：撤销 Token（安全措施）

如果 Token 已经泄露到 GitHub：

1. **访问**：https://github.com/settings/tokens
2. **找到泄露的 Token**
3. **点击 "Delete"** 删除旧 Token
4. **生成新的 Token**
5. **更新 `license_config.py`**
6. **更新 GitHub Secret**

## 📋 最佳实践

### 1. 使用环境变量

**本地开发**：
```python
# license_config.py（永远不提交到 Git）
GITHUB_TOKEN = "ghp_你的token"
```

**文档中**：
```markdown
- **Secret**: `你的GitHub Token`
```

### 2. 配置 .gitignore

确保 `.gitignore` 包含：
```gitignore
# 授权配置（敏感信息）
license_config.py
.gist_config
.docproc/
.docproc_cache/
```

### 3. 验证提交前的内容

```bash
# 检查暂存区内容
git diff --cached

# 搜索可能的 Token
git diff --cached | grep -i "ghp_"
```

### 4. 使用占位符

在文档中总是使用占位符：
- `你的GitHub Token`
- `ghp_你的token`
- `<YOUR_TOKEN_HERE>`
- `从 license_config.py 复制`

## 🔍 检查清单

提交前检查：
- [ ] 文档中没有真实的 Token
- [ ] `license_config.py` 在 `.gitignore` 中
- [ ] 使用 `git diff --cached` 检查暂存内容
- [ ] 搜索 `ghp_` 确认没有 Token

推送前检查：
- [ ] 本地提交历史没有 Token
- [ ] 使用 `git log -p` 检查最近的提交内容

## 📊 Token 管理策略

| 环境 | Token 存储位置 | 是否提交到 Git | 安全措施 |
|------|--------------|--------------|---------|
| 本地开发 | `license_config.py` | ❌ 不提交 | `.gitignore` |
| GitHub Actions | GitHub Secrets | ✅ Secret 安全 | 加密存储 |
| 文档说明 | 占位符 | ✅ 可以提交 | 不包含真实值 |
| 用户 exe | 打包时内置 | - | 只读，不可修改 |

## 🎯 快速修复流程

如果不小心提交了 Token：

```bash
# 1. 立即重置
git reset --soft HEAD~1

# 2. 修改文件，移除 Token
# （编辑文件，使用占位符替换真实 Token）

# 3. 重新提交
git add -A
git commit -m "🔐 修复敏感信息"

# 4. 推送（如果需要强制推送）
git push origin main --force-with-lease

# 5. 撤销旧 Token，生成新 Token
# 访问：https://github.com/settings/tokens
```

## 🚨 紧急情况

如果 Token 已经泄露并推送到 GitHub：

1. **立即删除 Token**：https://github.com/settings/tokens
2. **生成新 Token**
3. **清除 Git 历史**（使用 `git reset` 或 `git filter-branch`）
4. **强制推送**：`git push --force-with-lease`
5. **更新所有使用该 Token 的地方**

## ✅ 当前状态

- ✅ `.gitignore` 已配置
- ✅ `license_config.py` 不提交到 Git
- ✅ 文档中使用占位符
- ✅ Git 历史已清理
- ✅ 代码已成功推送

**记住：永远不要在提交到 Git 的文件中包含真实的 Token！** 🔐
