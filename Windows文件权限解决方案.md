# Windows 文件权限问题最终解决方案

## 问题分析

在 Windows 系统上，打包的 exe 文件可能无法写入 `%APPDATA%\.docproc\.lic` 配置文件，原因包括：

1. ❌ **杀毒软件拦截**：某些杀毒软件会阻止 exe 写入 APPDATA
2. ❌ **UAC 权限限制**：用户账户控制可能阻止文件创建
3. ❌ **环境变量未设置**：某些精简版 Windows 可能缺少 APPDATA 环境变量
4. ❌ **文件夹权限问题**：APPDATA 目录可能没有写入权限
5. ❌ **网络/域环境**：企业环境可能有组策略限制

## ✅ 解决方案：多重存储位置策略

### 核心思想
- 提供 **5 个备选存储位置**（Windows）
- 程序启动时**自动检测**可写位置
- 支持**数据迁移**：从旧位置自动迁移到新位置
- **原子写入**：使用临时文件+重命名保证数据完整性
- **立即验证**：每次写入后立即读取验证
- **3 次重试**：写入失败自动重试

### Windows 存储位置优先级

```
位置1: %APPDATA%\.docproc\.lic        (推荐，用户数据目录)
位置2: %LOCALAPPDATA%\.docproc\.lic   (本地应用数据)
位置3: %USERPROFILE%\.docproc\.lic    (用户主目录)
位置4: exe所在目录\.config\.lic        (便携模式)
位置5: %PROGRAMDATA%\.docproc\.lic    (公共数据目录)
备用: %TEMP%\.docproc_lic              (临时目录，最后手段)
```

### 工作流程

```
程序启动
    ↓
遍历所有位置
    ↓
测试写入权限
    ↓
找到第一个可写位置 ✅
    ↓
检查其他位置是否有旧配置
    ↓
如果有，自动迁移数据
    ↓
使用当前位置进行读写
```

## 技术实现

### 1. 自动位置检测

```python
def __init__(self):
    self.storage_locations = self._get_storage_locations()
    
    for location in self.storage_locations:
        try:
            # 测试写入权限
            os.makedirs(location['dir'], exist_ok=True)
            test_file = os.path.join(location['dir'], '.test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            
            # 成功！使用这个位置
            self.config_dir = location['dir']
            self.config_file = location['file']
            break
        except:
            continue
```

### 2. 原子写入 + 验证

```python
def save_usage_data(self, data: dict):
    for attempt in range(3):  # 最多重试 3 次
        # 写入临时文件
        temp_file = self.config_file + '.tmp'
        with open(temp_file, 'w') as f:
            f.write(encrypted)
            f.flush()
            os.fsync(f.fileno())  # 强制同步到磁盘
        
        # 原子替换
        os.rename(temp_file, self.config_file)
        
        # 立即验证
        verify_data = self.load_usage_data()
        if verify_data.get('count') == data.get('count'):
            return True  # 验证成功
```

### 3. 数据迁移

```python
def load_usage_data(self):
    # 首先从当前位置加载
    if os.path.exists(self.config_file):
        return self._load_from_file(self.config_file)
    
    # 尝试从其他所有位置加载（迁移）
    for location in self.storage_locations:
        if os.path.exists(location['file']):
            data = self._load_from_file(location['file'])
            if data:
                # 迁移到当前位置
                self.save_usage_data(data)
                return data
```

## 优势

✅ **兼容性强**：支持各种 Windows 环境（标准、精简、域、便携）
✅ **容错性高**：一个位置失败自动尝试下一个
✅ **数据安全**：原子写入 + 立即验证，防止数据损坏
✅ **用户友好**：自动迁移，用户无感知
✅ **调试清晰**：详细日志输出，便于排查问题

## 测试验证

### 本地测试
```bash
# macOS/Linux
python test_save_verify.py

# Windows
test_windows_save.bat
```

### 测试覆盖
- ✅ 多次连续写入测试
- ✅ 程序重启后数据持久化测试
- ✅ 计数累加正确性测试
- ✅ 文件损坏恢复测试
- ✅ 权限问题降级测试

## 使用说明

### 开发者
1. 代码已更新，直接使用即可
2. 所有测试通过后提交到 GitHub
3. GitHub Actions 自动构建 Windows exe

### 用户
1. 下载 exe 文件
2. 双击运行（无需管理员权限）
3. 程序自动选择最佳存储位置
4. 所有操作透明，无需手动配置

## 排查问题

如果在 Windows 上仍然无法计数，运行诊断：

```bash
# 使用 --console 模式运行
pyinstaller --clean --onefile --console document_processor.py

# 查看日志输出
DocumentProcessor.exe > debug.log 2>&1
```

查看日志中的：
- `[授权] ✅ 使用存储位置: XXX` - 确认使用了哪个位置
- `[授权] ✅✅ 验证成功: count=X` - 确认写入成功
- `[授权] ❌ XXX` - 查看具体错误信息

## 最坏情况

即使所有位置都失败（极端情况），程序会：
1. 使用临时目录 `%TEMP%\.docproc_lic`
2. 每次重启后临时目录可能清空，计数重置
3. **但程序仍然可以正常使用**，不会因为授权问题而无法运行

这确保了程序的可用性优先于授权限制。
