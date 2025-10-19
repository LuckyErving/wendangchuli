# 文档处理器 - 文档自动排序合并工具

## ✨ 新功能 (v1.1.0)

### 🔍 启动时自动检测Word转换器

程序现在会在启动时自动检测Word转换器是否可用：

**✅ 检测成功**：
- Windows: 检测到Microsoft Word
- macOS: 检测到LibreOffice
- 界面顶部显示绿色提示
- 所有功能正常

**⚠️ 检测失败**：
- 界面顶部显示橙色警告
- 点击"查看详细说明"按钮查看解决方案
- PDF和图片仍可正常处理
- Word文档会被跳过

---

## 功能说明

这是一个基于tkinter的Python图形界面程序，可以自动处理文件夹中的文档，按指定顺序排列并合并为一个PDF文件。

**特点**：
- ✅ 无需解压RAR文件，直接处理文件夹
- ✅ 支持Windows和macOS系统
- ✅ 可打包为独立的.exe可执行文件（Windows）
- ✅ 自动识别文档类型并排序
- ✅ 支持多种文档格式（PDF、Word、图片）

## 文档排序规则

程序会按以下顺序处理文档：

1. 申请书
2. 户主声明书
3. 承包方调查表
4. 承包地块调查表（可能有多个，顺序不限）
5. 公示结果归户表
6. 公示无异议声明书
7. 土地承包合同书（**会自动输出4份副本**）
8. 登记簿
9. 地块示意图（JPG格式，文件名以DKSYT开始，按尾部数字从小到大排序）
10. 确权登记声明书
11. 承诺书（支持DOCX格式）

## 系统要求

- Python 3.7+
- Windows 10/11 或 macOS

## 依赖安装

### Windows系统

#### 方法一：自动安装（推荐）

1. 双击运行 `install_windows.bat`
2. 等待安装完成

#### 方法二：手动安装

1. 安装Python 3.7+：https://www.python.org/downloads/
2. 打开命令提示符，执行：

```batch
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
```

3. （可选）安装WinRAR：https://www.winrar.com/
   - 或者使用Python的rarfile库（已包含在requirements.txt中）

### macOS系统

#### 1. Python依赖包

```bash
source /Users/ervin/Studio/zPlayground/.venv/bin/activate
pip install -r requirements.txt
```

#### 2. 系统工具

安装unar（解压RAR文件）：

```bash
brew install unar
```

安装LibreOffice（转换Word文档为PDF）：

```bash
brew install --cask libreoffice
```

或者从官网下载：https://www.libreoffice.org/download/download/

## 使用方法

### Windows系统

#### 方法一：双击运行（推荐）

直接双击 `run.bat` 文件

#### 方法二：命令行运行

```batch
call venv\Scripts\activate.bat
python document_processor.py
```

### macOS系统

```bash
source /Users/ervin/Studio/zPlayground/.venv/bin/activate
cd /Users/ervin/Studio/zPlayground/part-time/wendangchuli
python document_processor.py
```

### 操作步骤

1. 点击"浏览"按钮选择要处理的RAR压缩包
2. 选择输出PDF文件的保存位置（可以自动生成）
3. 点击"开始处理"按钮
4. 等待进度条完成
5. 处理完成后会弹出提示框

## 跨平台部署说明

### 重要提示

由于你在 **M1 Mac** 上开发，无法直接打包Windows可执行文件。需要按以下步骤操作：

### 步骤1：在Mac上准备项目

1. 确保所有代码已完成
2. 将整个项目文件夹复制到Windows电脑

### 步骤2：在Windows上打包为可执行文件

将项目文件夹复制到Windows电脑后：

#### 自动安装并打包

1. 双击运行 `install_windows.bat` - 安装所有依赖
2. 双击运行 `build_exe.bat` - 打包为exe文件
3. 在 `dist` 文件夹中找到 `文档处理器.exe`

#### 手动打包

```batch
REM 1. 安装依赖
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt

REM 2. 打包
pip install pyinstaller
pyinstaller document_processor.spec
```

打包完成后，`文档处理器.exe` 可以复制到任何Windows电脑上运行，无需安装Python。

### 步骤3：直接使用（不打包）

如果不想打包，也可以在Windows上直接运行Python脚本：

1. 双击运行 `install_windows.bat`
2. 双击运行 `run.bat`

## 支持的文件格式

- **文档**：PDF、DOC、DOCX
- **图片**：JPG、JPEG、PNG、BMP、TIFF

## 文件命名规则

程序通过文件名中的关键字来识别文档类型：

- 申请书：文件名包含"申请书"
- 户主声明书：文件名包含"户主声明书"
- 承包方调查表：文件名包含"承包方调查表"
- 承包地块调查表：文件名包含"承包地块调查表"
- 公示结果归户表：文件名包含"公示结果归户表"
- 公示无异议声明书：文件名包含"公示无异议声明书"
- 土地承包合同书：文件名包含"土地承包合同书"或"合同书"
- 登记簿：文件名包含"登记簿"
- 地块示意图：文件名匹配"DKSYT数字"格式（如DKSYT01、DKSYT02等）
- 确权登记声明书：文件名包含"确权登记声明书"
- 承诺书：文件名包含"承诺书"

## 注意事项

1. **土地承包合同书**会在PDF中自动重复4次
2. **地块示意图**按文件名尾部的两位数字排序（从小到大）
3. 处理过程中会创建临时文件，完成后自动清理
4. 确保有足够的磁盘空间用于临时文件
5. Word文档转换需要安装LibreOffice

## 故障排除

### Windows系统

#### 问题1：Word文档转换失败

**错误信息**：Windows系统需要安装: pip install docx2pdf

**解决方法**：
```batch
pip install docx2pdf
```

如果还是失败，确保安装了Microsoft Word，然后运行：
```batch
pip install pywin32
```

#### 问题2：找不到Python

**解决方法**：
- 从 https://www.python.org/downloads/ 下载并安装Python
- 安装时勾选"Add Python to PATH"

### macOS系统

#### 问题1：Word文档转换失败

**错误信息**：soffice命令未找到

**解决方法**：
```bash
# 安装LibreOffice
brew install --cask libreoffice

# 或者创建软链接（如果已安装但命令不可用）
sudo ln -s /Applications/LibreOffice.app/Contents/MacOS/soffice /usr/local/bin/soffice
```

### 通用问题

#### 问题：某些文件未被识别

**解决方法**：检查文件名是否包含正确的关键字，参考上述"文件命名规则"

## 技术细节

- **GUI框架**：tkinter
- **PDF处理**：PyPDF2
- **图片转PDF**：img2pdf、Pillow
- **文档转换**：LibreOffice
- **压缩包解压**：unar

## 项目结构

```
.
├── document_processor.py   # 主程序
├── requirements.txt        # Python依赖
└── README.md              # 说明文档
```

## 许可证

MIT License
