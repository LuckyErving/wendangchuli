#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档处理器 - 自动将压缩包中的文档按指定顺序合并为PDF
"""

import os
import re
import shutil
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import subprocess
from typing import List, Tuple
from PIL import Image
import img2pdf

# 消除macOS的Tk废弃警告
os.environ['TK_SILENCE_DEPRECATION'] = '1'


class DocumentProcessor:
    """文档处理核心类"""
    
    # 文档类型关键字匹配规则
    DOC_PATTERNS = {
        '申请书': r'申请书',
        '户主声明书': r'户主声明书',
        '承包方调查表': r'承包方调查表',
        '承包地块调查表': r'承包地块调查表',
        '公示结果归户表': r'公示结果归户表',
        '公示无异议声明书': r'公示无异议声明书',
        '土地承包合同书': r'土地承包合同书|合同书',
        '登记簿': r'登记簿',
        '地块示意图': r'DKSYT\d{2}',
        '确权登记声明书': r'确权登记声明书',
        '承诺书': r'承诺书',
    }
    
    def __init__(self):
        self.temp_dir = None
    
    def find_files(self, directory: str) -> List[str]:
        """递归查找所有文件"""
        files = []
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                if not filename.startswith('.'):  # 忽略隐藏文件
                    files.append(os.path.join(root, filename))
        return files
    
    def classify_file(self, filepath: str) -> Tuple[str, str]:
        """分类文件，返回(类型, 文件路径)"""
        filename = os.path.basename(filepath)
        
        for doc_type, pattern in self.DOC_PATTERNS.items():
            if re.search(pattern, filename, re.IGNORECASE):
                return (doc_type, filepath)
        
        return ('未分类', filepath)
    
    def sort_files(self, files: List[str]) -> dict:
        """按要求对文件分类和排序"""
        classified = {
            '申请书': [],
            '户主声明书': [],
            '承包方调查表': [],
            '承包地块调查表': [],
            '公示结果归户表': [],
            '公示无异议声明书': [],
            '土地承包合同书': [],
            '登记簿': [],
            '地块示意图': [],
            '确权登记声明书': [],
            '承诺书': [],
            '未分类': []
        }
        
        for filepath in files:
            doc_type, _ = self.classify_file(filepath)
            classified[doc_type].append(filepath)
        
        # 对地块示意图按编号排序
        if classified['地块示意图']:
            classified['地块示意图'].sort(key=lambda x: self._extract_plot_number(x))
        
        return classified
    
    def _extract_plot_number(self, filepath: str) -> int:
        """从地块示意图文件名中提取编号"""
        filename = os.path.basename(filepath)
        match = re.search(r'DKSYT(\d{2})', filename, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 999  # 默认放在最后
    
    def convert_to_pdf(self, filepath: str, output_pdf: str) -> bool:
        """将文档转换为PDF"""
        ext = os.path.splitext(filepath)[1].lower()
        
        import platform
        is_windows = platform.system() == 'Windows'
        
        try:
            if ext in ['.pdf']:
                # 已经是PDF，直接复制
                shutil.copy(filepath, output_pdf)
                return True
                
            elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                # 图片转PDF
                with open(output_pdf, 'wb') as f:
                    img = Image.open(filepath)
                    # 转换为RGB模式（如果需要）
                    if img.mode in ('RGBA', 'LA', 'P'):
                        img = img.convert('RGB')
                    pdf_bytes = img2pdf.convert(filepath)
                    f.write(pdf_bytes)
                return True
                
            elif ext in ['.doc', '.docx']:
                # Word文档转PDF
                if is_windows:
                    # Windows系统 - 尝试使用docx2pdf
                    try:
                        from docx2pdf import convert
                        convert(filepath, output_pdf)
                        return os.path.exists(output_pdf)
                    except ImportError:
                        raise Exception("Windows系统需要安装: pip install docx2pdf")
                    except Exception as e:
                        print(f"docx2pdf转换失败，尝试使用win32com: {str(e)}")
                        # 备用方案：使用win32com（需要安装Microsoft Word）
                        try:
                            import win32com.client
                            word = win32com.client.Dispatch("Word.Application")
                            word.visible = False
                            doc = word.Documents.Open(os.path.abspath(filepath))
                            doc.SaveAs(os.path.abspath(output_pdf), FileFormat=17)  # 17 = PDF
                            doc.Close()
                            word.Quit()
                            return True
                        except Exception as e2:
                            raise Exception(f"Word转换失败: {str(e2)}。请安装Microsoft Word或运行: pip install docx2pdf")
                else:
                    # macOS/Linux系统 - 使用LibreOffice
                    result = subprocess.run(
                        ['soffice', '--headless', '--convert-to', 'pdf', '--outdir',
                         os.path.dirname(output_pdf), filepath],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    # LibreOffice生成的文件名
                    expected_pdf = os.path.join(
                        os.path.dirname(output_pdf),
                        os.path.splitext(os.path.basename(filepath))[0] + '.pdf'
                    )
                    
                    if os.path.exists(expected_pdf):
                        if expected_pdf != output_pdf:
                            shutil.move(expected_pdf, output_pdf)
                        return True
                        
                    return False
                
            else:
                print(f"不支持的文件格式: {ext}")
                return False
                
        except Exception as e:
            print(f"转换失败 {filepath}: {str(e)}")
            return False
    
    def merge_pdfs(self, pdf_files: List[str], output_path: str):
        """合并多个PDF文件"""
        try:
            # 使用PyPDF2合并
            from PyPDF2 import PdfMerger
            
            merger = PdfMerger()
            for pdf_file in pdf_files:
                if os.path.exists(pdf_file):
                    merger.append(pdf_file)
            
            merger.write(output_path)
            merger.close()
            
        except Exception as e:
            raise Exception(f"PDF合并失败: {str(e)}")
    
    def process_folder(self, folder_path: str, output_pdf: str, progress_callback=None):
        """处理文件夹的主流程"""
        try:
            # 1. 验证文件夹
            if not os.path.isdir(folder_path):
                raise Exception("选择的路径不是有效的文件夹")
            
            if progress_callback:
                progress_callback(10, "正在扫描文件夹...")
            
            # 2. 查找所有文件
            if progress_callback:
                progress_callback(20, "正在扫描文件...")
            all_files = self.find_files(folder_path)
            
            # 3. 分类和排序
            if progress_callback:
                progress_callback(30, "正在分类文件...")
            classified = self.sort_files(all_files)
            
            # 4. 转换为PDF
            if progress_callback:
                progress_callback(40, "正在转换文档为PDF...")
            
            pdf_temp_dir = tempfile.mkdtemp(prefix='pdf_temp_')
            ordered_pdfs = []
            
            # 按指定顺序处理
            order = [
                '申请书', '户主声明书', '承包方调查表', '承包地块调查表',
                '公示结果归户表', '公示无异议声明书', '土地承包合同书',
                '登记簿', '地块示意图', '确权登记声明书', '承诺书'
            ]
            
            total_files = sum(len(classified[t]) for t in order)
            processed = 0
            
            for doc_type in order:
                files = classified[doc_type]
                
                for i, filepath in enumerate(files):
                    # 特殊处理：土地承包合同书输出4份
                    repeat_count = 4 if doc_type == '土地承包合同书' else 1
                    
                    for repeat in range(repeat_count):
                        output_name = f"{len(ordered_pdfs):03d}_{doc_type}_{i}_{repeat}.pdf"
                        output = os.path.join(pdf_temp_dir, output_name)
                        
                        if self.convert_to_pdf(filepath, output):
                            ordered_pdfs.append(output)
                    
                    processed += 1
                    if progress_callback:
                        progress = 40 + int((processed / total_files) * 40)
                        progress_callback(progress, f"正在处理: {doc_type}...")
            
            # 5. 合并PDF
            if progress_callback:
                progress_callback(90, "正在合并PDF...")
            self.merge_pdfs(ordered_pdfs, output_pdf)
            
            # 6. 清理临时文件
            if progress_callback:
                progress_callback(95, "正在清理临时文件...")
            shutil.rmtree(pdf_temp_dir, ignore_errors=True)
            
            if progress_callback:
                progress_callback(100, "完成！")
            
            return True
            
        except Exception as e:
            # 清理临时文件
            if pdf_temp_dir and os.path.exists(pdf_temp_dir):
                shutil.rmtree(pdf_temp_dir, ignore_errors=True)
            raise e


class DocumentProcessorGUI:
    """图形界面类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("文档处理器")
        
        # 设置窗口大小和背景
        self.root.geometry("700x600")
        self.root.configure(bg='#f5f5f5')
        self.root.resizable(True, True)
        
        # 初始化变量
        self.processor = DocumentProcessor()
        self.selected_folder = None
        self.output_pdf_path = None
        
        # 创建UI
        self.setup_ui()
        
        # 设置窗口居中（在UI创建后）
        self.center_window()
        
        # 强制更新
        self.root.update()
    
    def center_window(self):
        """将窗口居中显示"""
        self.root.update_idletasks()
        width = 700
        height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_ui(self):
        """设置用户界面"""
        # 配置根窗口的grid权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # 主框架 - 使用tk.Frame而不是ttk.Frame
        main_frame = tk.Frame(self.root, bg='white', padx=20, pady=20)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        
        # 标题
        title_label = tk.Label(
            main_frame,
            text="📄 文档自动排序合并工具",
            font=('Arial', 18, 'bold'),
            fg='#2c3e50',
            bg='white'
        )
        title_label.pack(pady=(0, 20), fill=tk.X)
        
        # 步骤1：上传文件夹
        step1_frame = tk.LabelFrame(
            main_frame, 
            text="步骤 1：选择文档文件夹", 
            font=('Arial', 11, 'bold'),
            bg='white',
            fg='#34495e',
            padx=15,
            pady=15
        )
        step1_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.folder_label = tk.Label(
            step1_frame, 
            text="📁 未选择文件夹",
            font=('Arial', 10),
            fg='gray',
            bg='white'
        )
        self.folder_label.pack(anchor=tk.W, pady=5)
        
        upload_button = tk.Button(
            step1_frame, 
            text="📂 上传文件夹",
            command=self.upload_folder,
            font=('Arial', 11),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2'
        )
        upload_button.pack(pady=10)
        
        # 文件统计信息
        self.file_count_label = tk.Label(
            step1_frame,
            text="",
            font=('Arial', 9),
            fg='#7f8c8d',
            bg='white'
        )
        self.file_count_label.pack(anchor=tk.W, pady=5)
        
        # 步骤2：处理文档
        step2_frame = tk.LabelFrame(
            main_frame, 
            text="步骤 2：处理文档", 
            font=('Arial', 11, 'bold'),
            bg='white',
            fg='#34495e',
            padx=15,
            pady=15
        )
        step2_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.process_button = tk.Button(
            step2_frame,
            text="🚀 开始处理",
            command=self.process,
            font=('Arial', 11),
            bg='#2ecc71',
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2',
            state='disabled'
        )
        self.process_button.pack(pady=10)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            step2_frame,
            variable=self.progress_var,
            maximum=100,
            length=600,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, pady=10)
        
        # 状态标签
        self.status_var = tk.StringVar(value="等待选择文件夹...")
        status_label = tk.Label(
            step2_frame, 
            textvariable=self.status_var,
            font=('Arial', 9),
            fg='#7f8c8d',
            bg='white'
        )
        status_label.pack(pady=5)
        
        # 步骤3：导出PDF
        step3_frame = ttk.LabelFrame(main_frame, text="步骤 3：导出PDF", padding="15")
        step3_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        step3_frame.columnconfigure(0, weight=1)
        
        self.export_info_label = ttk.Label(
            step3_frame,
            text="处理完成后可以导出PDF文件",
            font=('Arial', 10),
            foreground='gray'
        )
        self.export_info_label.grid(row=0, column=0, pady=5)
        
        self.export_button = ttk.Button(
            step3_frame,
            text="� 导出PDF",
            command=self.export_pdf,
            width=20,
            state='disabled'
        )
        self.export_button.grid(row=1, column=0, pady=10)
        
        # 说明文本
        help_frame = ttk.LabelFrame(main_frame, text="📖 使用说明", padding="10")
        help_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        help_text = """文档自动排序规则：
申请书 → 户主声明书 → 承包方调查表 → 承包地块调查表 → 公示结果归户表 → 
公示无异议声明书 → 土地承包合同书(×4份) → 登记簿 → 地块示意图(按编号) → 
确权登记声明书 → 承诺书

支持格式：PDF、Word (DOC/DOCX)、图片 (JPG/PNG/BMP/TIFF)"""
        
        help_label = ttk.Label(
            help_frame, 
            text=help_text, 
            justify=tk.LEFT, 
            foreground='#34495e',
            font=('Arial', 9)
        )
        help_label.grid(row=0, column=0, sticky=tk.W)
        
    def upload_folder(self):
        """上传文件夹"""
        foldername = filedialog.askdirectory(
            title="选择包含文档的文件夹"
        )
        if foldername:
            self.selected_folder = foldername
            folder_name = os.path.basename(foldername)
            self.folder_label.config(
                text=f"📁 已选择：{folder_name}",
                foreground='#27ae60'
            )
            
            # 统计文件数量
            try:
                all_files = self.processor.find_files(foldername)
                file_count = len(all_files)
                self.file_count_label.config(
                    text=f"找到 {file_count} 个文件"
                )
                
                # 启用处理按钮
                self.process_button.config(state='normal')
                self.status_var.set("✅ 已选择文件夹，可以开始处理")
                
            except Exception as e:
                messagebox.showerror("错误", f"读取文件夹失败：{str(e)}")
    
    def browse_input(self):
        """浏览输入文件夹（保留兼容性）"""
        self.upload_folder()
    
    def export_pdf(self):
        """导出PDF文件"""
        if not self.output_pdf_path or not os.path.exists(self.output_pdf_path):
            messagebox.showerror("错误", "没有可导出的PDF文件")
            return
        
        # 选择保存位置
        save_path = filedialog.asksaveasfilename(
            title="保存PDF文件",
            defaultextension=".pdf",
            filetypes=[("PDF文件", "*.pdf")],
            initialfile=os.path.basename(self.output_pdf_path)
        )
        
        if save_path:
            try:
                # 复制PDF到选择的位置
                shutil.copy(self.output_pdf_path, save_path)
                messagebox.showinfo(
                    "成功", 
                    f"PDF已成功导出到：\n{save_path}\n\n是否打开文件所在文件夹？"
                )
                
                # 打开文件所在文件夹
                import platform
                system = platform.system()
                folder_path = os.path.dirname(save_path)
                
                if system == 'Windows':
                    os.startfile(folder_path)
                elif system == 'Darwin':  # macOS
                    subprocess.run(['open', folder_path])
                else:  # Linux
                    subprocess.run(['xdg-open', folder_path])
                    
            except Exception as e:
                messagebox.showerror("错误", f"导出失败：{str(e)}")
    
    def browse_output(self):
        """浏览输出文件（保留兼容性）"""
        self.export_pdf()
    
    def update_progress(self, value: int, message: str):
        """更新进度"""
        self.progress_var.set(value)
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def process(self):
        """处理按钮点击事件"""
        # 验证输入
        if not self.selected_folder:
            messagebox.showerror("错误", "请先上传文件夹")
            return
        
        if not os.path.exists(self.selected_folder):
            messagebox.showerror("错误", "文件夹不存在")
            return
        
        if not os.path.isdir(self.selected_folder):
            messagebox.showerror("错误", "请选择文件夹而不是文件")
            return
        
        # 创建临时输出路径
        temp_output = tempfile.mktemp(suffix='.pdf', prefix='doc_processor_')
        
        # 禁用按钮
        self.process_button.config(state='disabled')
        self.export_button.config(state='disabled')
        
        try:
            # 开始处理
            self.processor.process_folder(
                self.selected_folder,
                temp_output,
                progress_callback=self.update_progress
            )
            
            # 保存输出路径
            self.output_pdf_path = temp_output
            
            # 更新UI
            self.status_var.set("✅ 处理完成！可以导出PDF了")
            self.export_button.config(state='normal')
            self.export_info_label.config(
                text="✅ PDF已生成，点击下方按钮导出",
                foreground='#27ae60'
            )
            
            messagebox.showinfo(
                "成功", 
                "文档处理完成！\n\n请点击下方的\"导出PDF\"按钮保存文件。"
            )
            
        except Exception as e:
            messagebox.showerror("错误", f"处理失败：\n{str(e)}")
            self.status_var.set(f"❌ 错误: {str(e)}")
            
        finally:
            # 恢复处理按钮
            self.process_button.config(state='normal')
            self.progress_var.set(0)


def main():
    """主函数"""
    root = tk.Tk()
    
    # 设置窗口背景色
    root.configure(bg='#f0f0f0')
    
    # 强制刷新
    root.update_idletasks()
    
    app = DocumentProcessorGUI(root)
    
    # 确保窗口可见
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    
    root.mainloop()


if __name__ == "__main__":
    main()
