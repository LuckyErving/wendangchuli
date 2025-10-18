#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档处理器 - 简洁版本（解决透明窗口问题）
"""

import os
import re
import shutil
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox
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
                if not filename.startswith('.'):
                    files.append(os.path.join(root, filename))
        return files
    
    def classify_file(self, filepath: str) -> Tuple[str, str]:
        """分类文件"""
        filename = os.path.basename(filepath)
        for doc_type, pattern in self.DOC_PATTERNS.items():
            if re.search(pattern, filename, re.IGNORECASE):
                return (doc_type, filepath)
        return ('未分类', filepath)
    
    def sort_files(self, files: List[str]) -> dict:
        """按要求对文件分类和排序"""
        classified = {
            '申请书': [], '户主声明书': [], '承包方调查表': [], '承包地块调查表': [],
            '公示结果归户表': [], '公示无异议声明书': [], '土地承包合同书': [],
            '登记簿': [], '地块示意图': [], '确权登记声明书': [], '承诺书': [], '未分类': []
        }
        
        for filepath in files:
            doc_type, _ = self.classify_file(filepath)
            classified[doc_type].append(filepath)
        
        if classified['地块示意图']:
            classified['地块示意图'].sort(key=lambda x: self._extract_plot_number(x))
        
        return classified
    
    def _extract_plot_number(self, filepath: str) -> int:
        """从地块示意图文件名中提取编号"""
        filename = os.path.basename(filepath)
        match = re.search(r'DKSYT(\d{2})', filename, re.IGNORECASE)
        return int(match.group(1)) if match else 999
    
    def convert_to_pdf(self, filepath: str, output_pdf: str) -> bool:
        """将文档转换为PDF"""
        ext = os.path.splitext(filepath)[1].lower()
        import platform
        is_windows = platform.system() == 'Windows'
        
        try:
            if ext in ['.pdf']:
                shutil.copy(filepath, output_pdf)
                return True
            elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                with open(output_pdf, 'wb') as f:
                    img = Image.open(filepath)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        img = img.convert('RGB')
                    pdf_bytes = img2pdf.convert(filepath)
                    f.write(pdf_bytes)
                return True
            elif ext in ['.doc', '.docx']:
                if is_windows:
                    try:
                        from docx2pdf import convert
                        convert(filepath, output_pdf)
                        return os.path.exists(output_pdf)
                    except:
                        return False
                else:
                    result = subprocess.run(
                        ['soffice', '--headless', '--convert-to', 'pdf', '--outdir',
                         os.path.dirname(output_pdf), filepath],
                        capture_output=True, timeout=30
                    )
                    expected_pdf = os.path.join(
                        os.path.dirname(output_pdf),
                        os.path.splitext(os.path.basename(filepath))[0] + '.pdf'
                    )
                    if os.path.exists(expected_pdf):
                        if expected_pdf != output_pdf:
                            shutil.move(expected_pdf, output_pdf)
                        return True
                return False
            return False
        except Exception as e:
            print(f"转换失败 {filepath}: {str(e)}")
            return False
    
    def merge_pdfs(self, pdf_files: List[str], output_path: str):
        """合并多个PDF文件"""
        from PyPDF2 import PdfMerger
        merger = PdfMerger()
        for pdf_file in pdf_files:
            if os.path.exists(pdf_file):
                merger.append(pdf_file)
        merger.write(output_path)
        merger.close()
    
    def process_folder(self, folder_path: str, output_pdf: str, progress_callback=None):
        """处理文件夹的主流程"""
        try:
            if not os.path.isdir(folder_path):
                raise Exception("选择的路径不是有效的文件夹")
            
            if progress_callback:
                progress_callback(10, "正在扫描文件...")
            
            all_files = self.find_files(folder_path)
            classified = self.sort_files(all_files)
            
            if progress_callback:
                progress_callback(30, "正在转换文档...")
            
            pdf_temp_dir = tempfile.mkdtemp(prefix='pdf_temp_')
            ordered_pdfs = []
            
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
                    repeat_count = 4 if doc_type == '土地承包合同书' else 1
                    for repeat in range(repeat_count):
                        output_name = f"{len(ordered_pdfs):03d}_{doc_type}_{i}_{repeat}.pdf"
                        output = os.path.join(pdf_temp_dir, output_name)
                        if self.convert_to_pdf(filepath, output):
                            ordered_pdfs.append(output)
                    processed += 1
                    if progress_callback:
                        progress = 30 + int((processed / total_files) * 50)
                        progress_callback(progress, f"正在处理: {doc_type}...")
            
            if progress_callback:
                progress_callback(90, "正在合并PDF...")
            self.merge_pdfs(ordered_pdfs, output_pdf)
            
            shutil.rmtree(pdf_temp_dir, ignore_errors=True)
            
            if progress_callback:
                progress_callback(100, "完成！")
            
            return True
        except Exception as e:
            raise e


class SimpleGUI:
    """简洁的图形界面"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("文档处理器")
        self.root.geometry("600x500")
        
        # 强制设置背景色
        self.root.configure(bg='#e8e8e8')
        
        self.processor = DocumentProcessor()
        self.selected_folder = None
        self.output_pdf_path = None
        
        self.create_widgets()
        self.center_window()
    
    def center_window(self):
        """窗口居中"""
        self.root.update_idletasks()
        width = 600
        height = 500
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """创建所有组件"""
        # 标题
        title = tk.Label(
            self.root,
            text="文档自动排序合并工具",
            font=("Arial", 20, "bold"),
            bg='#e8e8e8',
            fg='#2c3e50'
        )
        title.pack(pady=20)
        
        # 步骤1
        frame1 = tk.LabelFrame(
            self.root,
            text="步骤 1：选择文档文件夹",
            font=("Arial", 12, "bold"),
            bg='white',
            fg='#34495e',
            padx=20,
            pady=15
        )
        frame1.pack(fill=tk.X, padx=20, pady=10)
        
        self.folder_label = tk.Label(
            frame1,
            text="未选择文件夹",
            font=("Arial", 10),
            bg='white',
            fg='gray'
        )
        self.folder_label.pack(pady=5)
        
        btn1 = tk.Button(
            frame1,
            text="选择文件夹",
            command=self.select_folder,
            font=("Arial", 11),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=8
        )
        btn1.pack(pady=5)
        
        self.file_count_label = tk.Label(
            frame1,
            text="",
            font=("Arial", 9),
            bg='white',
            fg='#7f8c8d'
        )
        self.file_count_label.pack(pady=5)
        
        # 步骤2
        frame2 = tk.LabelFrame(
            self.root,
            text="步骤 2：处理文档",
            font=("Arial", 12, "bold"),
            bg='white',
            fg='#34495e',
            padx=20,
            pady=15
        )
        frame2.pack(fill=tk.X, padx=20, pady=10)
        
        self.process_btn = tk.Button(
            frame2,
            text="开始处理",
            command=self.process,
            font=("Arial", 11),
            bg='#2ecc71',
            fg='white',
            padx=20,
            pady=8,
            state='disabled'
        )
        self.process_btn.pack(pady=5)
        
        self.progress_label = tk.Label(
            frame2,
            text="等待选择文件夹...",
            font=("Arial", 9),
            bg='white',
            fg='#7f8c8d'
        )
        self.progress_label.pack(pady=5)
        
        # 步骤3
        frame3 = tk.LabelFrame(
            self.root,
            text="步骤 3：导出PDF",
            font=("Arial", 12, "bold"),
            bg='white',
            fg='#34495e',
            padx=20,
            pady=15
        )
        frame3.pack(fill=tk.X, padx=20, pady=10)
        
        self.export_label = tk.Label(
            frame3,
            text="处理完成后可以导出PDF",
            font=("Arial", 10),
            bg='white',
            fg='gray'
        )
        self.export_label.pack(pady=5)
        
        self.export_btn = tk.Button(
            frame3,
            text="导出PDF",
            command=self.export_pdf,
            font=("Arial", 11),
            bg='#e74c3c',
            fg='white',
            padx=20,
            pady=8,
            state='disabled'
        )
        self.export_btn.pack(pady=5)
    
    def select_folder(self):
        """选择文件夹"""
        folder = filedialog.askdirectory(title="选择包含文档的文件夹")
        if folder:
            self.selected_folder = folder
            name = os.path.basename(folder)
            self.folder_label.config(text=f"已选择: {name}", fg='#27ae60')
            
            try:
                files = self.processor.find_files(folder)
                self.file_count_label.config(text=f"找到 {len(files)} 个文件")
                self.process_btn.config(state='normal')
                self.progress_label.config(text="可以开始处理了")
            except Exception as e:
                messagebox.showerror("错误", f"读取文件夹失败: {str(e)}")
    
    def update_progress(self, value, message):
        """更新进度"""
        self.progress_label.config(text=message)
        self.root.update()
    
    def process(self):
        """处理文档"""
        if not self.selected_folder:
            messagebox.showerror("错误", "请先选择文件夹")
            return
        
        temp_output = tempfile.mktemp(suffix='.pdf')
        self.process_btn.config(state='disabled')
        self.export_btn.config(state='disabled')
        
        try:
            self.processor.process_folder(
                self.selected_folder,
                temp_output,
                progress_callback=self.update_progress
            )
            
            self.output_pdf_path = temp_output
            self.progress_label.config(text="处理完成！", fg='#27ae60')
            self.export_label.config(text="PDF已生成，点击下方导出", fg='#27ae60')
            self.export_btn.config(state='normal')
            
            messagebox.showinfo("成功", "文档处理完成！\n请点击\"导出PDF\"保存文件。")
        except Exception as e:
            messagebox.showerror("错误", f"处理失败: {str(e)}")
            self.progress_label.config(text=f"错误: {str(e)}", fg='red')
        finally:
            self.process_btn.config(state='normal')
    
    def export_pdf(self):
        """导出PDF"""
        if not self.output_pdf_path or not os.path.exists(self.output_pdf_path):
            messagebox.showerror("错误", "没有可导出的PDF")
            return
        
        save_path = filedialog.asksaveasfilename(
            title="保存PDF",
            defaultextension=".pdf",
            filetypes=[("PDF文件", "*.pdf")]
        )
        
        if save_path:
            try:
                shutil.copy(self.output_pdf_path, save_path)
                messagebox.showinfo("成功", f"PDF已导出到:\n{save_path}")
                
                # 打开文件夹
                import platform
                folder = os.path.dirname(save_path)
                if platform.system() == 'Darwin':
                    subprocess.run(['open', folder])
                elif platform.system() == 'Windows':
                    os.startfile(folder)
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")
    
    def run(self):
        """运行程序"""
        self.root.mainloop()


if __name__ == "__main__":
    print("正在启动文档处理器...")
    app = SimpleGUI()
    app.run()
