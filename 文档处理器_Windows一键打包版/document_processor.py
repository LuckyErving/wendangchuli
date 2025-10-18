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
        self.root.title("文档处理器 - RAR转PDF")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        self.processor = DocumentProcessor()
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(
            main_frame,
            text="文档自动排序合并工具",
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=20)
        
        # 输入文件夹选择
        ttk.Label(main_frame, text="文件夹路径:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.input_var = tk.StringVar()
        input_entry = ttk.Entry(main_frame, textvariable=self.input_var, width=40)
        input_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="浏览", command=self.browse_input).grid(row=1, column=2, pady=5)
        
        # 输出文件选择
        ttk.Label(main_frame, text="输出PDF路径:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.output_var = tk.StringVar()
        output_entry = ttk.Entry(main_frame, textvariable=self.output_var, width=40)
        output_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="浏览", command=self.browse_output).grid(row=2, column=2, pady=5)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            length=500
        )
        self.progress_bar.grid(row=3, column=0, columnspan=3, pady=20)
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=4, column=0, columnspan=3, pady=5)
        
        # 处理按钮
        self.process_button = ttk.Button(
            main_frame,
            text="开始处理",
            command=self.process,
            style='Accent.TButton'
        )
        self.process_button.grid(row=5, column=0, columnspan=3, pady=20)
        
        # 说明文本
        help_text = """
使用说明：
1. 选择包含文档的文件夹
2. 选择输出PDF文件的保存位置
3. 点击"开始处理"按钮
4. 等待处理完成

文档将按以下顺序排列：
申请书 → 户主声明书 → 承包方调查表 → 承包地块调查表 → 
公示结果归户表 → 公示无异议声明书 → 土地承包合同书(×4份) → 
登记簿 → 地块示意图 → 确权登记声明书 → 承诺书
        """
        help_label = ttk.Label(main_frame, text=help_text, justify=tk.LEFT, foreground='gray')
        help_label.grid(row=6, column=0, columnspan=3, pady=10)
        
    def browse_input(self):
        """浏览输入文件夹"""
        foldername = filedialog.askdirectory(
            title="选择包含文档的文件夹"
        )
        if foldername:
            self.input_var.set(foldername)
            # 自动设置输出文件名
            if not self.output_var.get():
                base_name = os.path.basename(foldername)
                output_path = os.path.join(
                    foldername,
                    f"{base_name}_合并.pdf"
                )
                self.output_var.set(output_path)
    
    def browse_output(self):
        """浏览输出文件"""
        filename = filedialog.asksaveasfilename(
            title="保存PDF文件",
            defaultextension=".pdf",
            filetypes=[("PDF文件", "*.pdf")]
        )
        if filename:
            self.output_var.set(filename)
    
    def update_progress(self, value: int, message: str):
        """更新进度"""
        self.progress_var.set(value)
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def process(self):
        """处理按钮点击事件"""
        input_path = self.input_var.get()
        output_path = self.output_var.get()
        
        # 验证输入
        if not input_path:
            messagebox.showerror("错误", "请选择输入文件夹")
            return
        
        if not output_path:
            messagebox.showerror("错误", "请选择输出PDF路径")
            return
        
        if not os.path.exists(input_path):
            messagebox.showerror("错误", "输入文件夹不存在")
            return
        
        if not os.path.isdir(input_path):
            messagebox.showerror("错误", "请选择文件夹而不是文件")
            return
        
        # 禁用按钮
        self.process_button.config(state='disabled')
        
        try:
            # 开始处理
            self.processor.process_folder(
                input_path,
                output_path,
                progress_callback=self.update_progress
            )
            
            messagebox.showinfo("成功", f"处理完成！\n输出文件：{output_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"处理失败：\n{str(e)}")
            self.status_var.set(f"错误: {str(e)}")
            
        finally:
            # 恢复按钮
            self.process_button.config(state='normal')
            self.progress_var.set(0)


def main():
    """主函数"""
    root = tk.Tk()
    app = DocumentProcessorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
