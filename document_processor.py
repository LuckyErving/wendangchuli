#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档处理器 
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
import hashlib
import json
import uuid
import platform
from datetime import datetime

# 消除macOS的Tk废弃警告
os.environ['TK_SILENCE_DEPRECATION'] = '1'


class LicenseManager:
    """设备授权管理器"""
    
    MAX_USAGE_COUNT = 200  # 最大使用次数
    
    def __init__(self):
        # 使用隐藏的配置文件存储使用记录
        if platform.system() == 'Windows':
            appdata = os.environ.get('APPDATA', '')
            if not appdata:
                # 备用方案：使用用户目录
                appdata = os.path.expanduser('~')
            self.config_dir = os.path.join(appdata, '.docproc')
        else:
            self.config_dir = os.path.join(os.path.expanduser('~'), '.docproc')
        
        print(f"[授权] 配置目录: {self.config_dir}")
        
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            print(f"[授权] 配置目录创建成功")
        except Exception as e:
            print(f"[授权] ⚠️ 创建配置目录失败: {e}")
        
        self.config_file = os.path.join(self.config_dir, '.lic')
        print(f"[授权] 配置文件: {self.config_file}")
    
    def get_mac_address(self):
        """获取设备MAC地址"""
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                           for elements in range(0, 48, 8)][::-1])
            return mac
        except:
            return None
    
    def _encrypt_data(self, data: dict) -> str:
        """简单加密数据（使用base64混淆）"""
        import base64
        json_str = json.dumps(data)
        # 多次base64编码混淆
        encrypted = json_str.encode('utf-8')
        for _ in range(3):
            encrypted = base64.b64encode(encrypted)
        return encrypted.decode('utf-8')
    
    def _decrypt_data(self, encrypted: str) -> dict:
        """解密数据"""
        import base64
        try:
            decrypted = encrypted.encode('utf-8')
            for _ in range(3):
                decrypted = base64.b64decode(decrypted)
            return json.loads(decrypted.decode('utf-8'))
        except:
            return None
    
    def _get_device_hash(self, mac: str) -> str:
        """生成设备指纹哈希"""
        # 使用MAC地址和一个盐值生成哈希
        salt = "doc_processor_v1_2025"
        return hashlib.sha256(f"{mac}{salt}".encode()).hexdigest()
    
    def load_usage_data(self):
        """加载使用记录"""
        if not os.path.exists(self.config_file):
            print(f"[授权] 配置文件不存在，首次使用")
            return None
        
        try:
            with open(self.config_file, 'r') as f:
                encrypted = f.read()
            data = self._decrypt_data(encrypted)
            if data:
                print(f"[授权] 配置加载成功，已使用 {data.get('count', 0)} 次")
            return data
        except Exception as e:
            print(f"[授权] ⚠️ 加载配置失败: {e}")
            return None
    
    def save_usage_data(self, data: dict):
        """保存使用记录"""
        try:
            print(f"[授权] 准备保存: count={data.get('count', 0)}")
            encrypted = self._encrypt_data(data)
            
            # 确保目录存在
            if not os.path.exists(self.config_dir):
                os.makedirs(self.config_dir, exist_ok=True)
                print(f"[授权] 重新创建配置目录")
            
            with open(self.config_file, 'w') as f:
                f.write(encrypted)
            
            print(f"[授权] ✅ 保存成功: {self.config_file}")
            
            # 设置为隐藏文件（Windows）
            if platform.system() == 'Windows':
                try:
                    import ctypes
                    ctypes.windll.kernel32.SetFileAttributesW(self.config_file, 2)  # FILE_ATTRIBUTE_HIDDEN
                    print(f"[授权] 文件已设置为隐藏")
                except Exception as e:
                    print(f"[授权] 设置隐藏属性失败: {e}")
        except Exception as e:
            print(f"[授权] ❌ 保存使用记录失败: {e}")
            import traceback
            traceback.print_exc()
    
    def check_device(self) -> Tuple[bool, str]:
        """
        仅检查设备绑定，不更新计数（用于程序启动时）
        返回: (是否允许使用, 消息)
        """
        mac = self.get_mac_address()
        if not mac:
            return False, "无法获取设备信息"
        
        device_hash = self._get_device_hash(mac)
        usage_data = self.load_usage_data()
        
        if usage_data is None:
            # 首次使用，初始化配置
            usage_data = {
                'device': device_hash,
                'count': 0,
                'first_use': datetime.now().isoformat(),
                'last_use': datetime.now().isoformat()
            }
            self.save_usage_data(usage_data)
            return True, f"首次使用"
        
        # 验证设备
        if usage_data.get('device') != device_hash:
            return False, "设备不匹配"
        
        return True, "设备验证成功"
    
    def check_and_update_usage(self) -> Tuple[bool, str]:
        """
        检查并更新使用次数（每次处理文档时调用）
        返回: (是否允许使用, 消息)
        """
        print(f"\n[授权] ========== 开始检查并更新使用次数 ==========")
        
        mac = self.get_mac_address()
        if not mac:
            print(f"[授权] ❌ 无法获取MAC地址")
            return False, "无法获取设备信息，程序无法运行"
        
        print(f"[授权] MAC地址: {mac}")
        
        device_hash = self._get_device_hash(mac)
        print(f"[授权] 设备哈希: {device_hash[:16]}...")
        
        usage_data = self.load_usage_data()
        
        if usage_data is None:
            # 不应该发生，但为了安全还是处理
            print(f"[授权] 配置不存在，初始化")
            usage_data = {
                'device': device_hash,
                'count': 0,
                'first_use': datetime.now().isoformat(),
                'last_use': datetime.now().isoformat()
            }
        
        # 验证设备
        if usage_data.get('device') != device_hash:
            print(f"[授权] ❌ 设备不匹配")
            return False, "设备已损坏"
        
        # 检查使用次数
        current_count = usage_data.get('count', 0)
        print(f"[授权] 当前使用次数: {current_count}/{self.MAX_USAGE_COUNT}")
        
        if current_count >= self.MAX_USAGE_COUNT:
            print(f"[授权] ❌ 已达到使用上限")
            return False, "程序已损坏"
        
        # 更新使用次数
        usage_data['count'] = current_count + 1
        usage_data['last_use'] = datetime.now().isoformat()
        
        print(f"[授权] 更新使用次数: {current_count} → {usage_data['count']}")
        
        self.save_usage_data(usage_data)
        
        remaining = self.MAX_USAGE_COUNT - usage_data['count']
        print(f"[授权] ✅ 检查通过，剩余次数: {remaining}")
        print(f"[授权] ========== 检查完成 ==========\n")
        
        return True, f"剩余次数: {remaining}"
    
    def get_usage_info(self) -> str:
        """获取使用信息"""
        usage_data = self.load_usage_data()
        if not usage_data:
            return f"剩余使用次数: {self.MAX_USAGE_COUNT}"
        
        count = usage_data.get('count', 0)
        remaining = self.MAX_USAGE_COUNT - count
        return f"已使用: {count} 次，剩余: {remaining} 次"


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
    
    @staticmethod
    def check_word_converter():
        """检测Word转换器是否可用"""
        import platform
        is_windows = platform.system() == 'Windows'
        
        if is_windows:
            # 检查Windows上的docx2pdf和Word
            try:
                import docx2pdf
                # 尝试检测Word是否安装（通过COM）
                try:
                    import win32com.client
                    word = win32com.client.Dispatch("Word.Application")
                    word.Quit()
                    return True, "✅ Microsoft Word 已安装"
                except:
                    return False, "⚠️ 未检测到 Microsoft Word\n\n程序无法转换 .docx 文件为PDF。\n\n解决方案：\n1. 安装 Microsoft Word (Office)\n2. 或手动将 .docx 转换为 .pdf\n\n其他文件(PDF、图片)可以正常处理。"
            except ImportError:
                return False, "⚠️ 缺少 docx2pdf 库"
        else:
            # 检查macOS/Linux上的LibreOffice
            try:
                result = subprocess.run(['which', 'soffice'], 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=5)
                if result.returncode == 0:
                    return True, "✅ LibreOffice 已安装"
                else:
                    return False, "⚠️ 未检测到 LibreOffice\n\n程序无法转换 .docx 文件为PDF。\n\n解决方案：\n安装 LibreOffice:\nbrew install --cask libreoffice\n\n或手动下载：\nhttps://www.libreoffice.org/\n\n其他文件(PDF、图片)可以正常处理。"
            except:
                return False, "⚠️ 未检测到 LibreOffice"
    
    def preprocess_word_files(self, folder_path: str, progress_callback=None):
        """预处理：将所有.doc和.docx文件转换为PDF并保存到同目录"""
        from docx import Document
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.pdfgen import canvas
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.units import inch
        import io
        
        print("\n" + "=" * 50)
        print("开始预处理Word文档...")
        print("=" * 50)
        
        # 查找所有.doc和.docx文件
        word_files = []
        for root, dirs, filenames in os.walk(folder_path):
            for filename in filenames:
                if (filename.lower().endswith('.docx') or filename.lower().endswith('.doc')) and not filename.startswith('~'):
                    filepath = os.path.join(root, filename)
                    word_files.append(filepath)
        
        if not word_files:
            print("没有找到Word文档（.doc/.docx），跳过预处理")
            return []
        
        print(f"找到 {len(word_files)} 个Word文档")
        converted_files = []
        
        for i, word_path in enumerate(word_files):
            try:
                filename = os.path.basename(word_path)
                print(f"\n[{i+1}/{len(word_files)}] 正在转换: {filename}")
                
                if progress_callback:
                    progress = int((i / len(word_files)) * 20)  # 预处理占20%
                    progress_callback(progress, f"预处理Word文档 ({i+1}/{len(word_files)})")
                
                # 生成PDF文件路径（同目录，同名，.pdf后缀）
                pdf_path = os.path.splitext(word_path)[0] + '.pdf'
                
                # 如果PDF已存在，跳过
                if os.path.exists(pdf_path):
                    print(f"  PDF已存在，跳过: {os.path.basename(pdf_path)}")
                    converted_files.append(pdf_path)
                    continue
                
                # 检查文件扩展名
                file_ext = os.path.splitext(word_path)[1].lower()
                
                # .doc文件无法直接用python-docx读取，跳过
                if file_ext == '.doc':
                    print(f"  ⚠️ .doc格式需要LibreOffice或Word转换，已跳过")
                    print(f"  提示: 请手动在Word中打开并另存为.docx或.pdf")
                    continue
                
                # 使用python-docx读取.docx内容
                doc = Document(word_path)
                
                # 创建PDF，使用支持中文的方式
                from reportlab.pdfbase.cidfonts import UnicodeCIDFont
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
                from reportlab.lib.enums import TA_LEFT, TA_CENTER
                
                # 创建PDF文档
                pdf_doc = SimpleDocTemplate(pdf_path, pagesize=A4)
                story = []
                
                # 注册中文字体
                pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
                
                # 创建样式
                styles = getSampleStyleSheet()
                chinese_style = ParagraphStyle(
                    'Chinese',
                    parent=styles['Normal'],
                    fontName='STSong-Light',
                    fontSize=12,
                    leading=20,
                    alignment=TA_LEFT,
                )
                
                title_style = ParagraphStyle(
                    'ChineseTitle',
                    parent=styles['Heading1'],
                    fontName='STSong-Light',
                    fontSize=16,
                    leading=24,
                    alignment=TA_CENTER,
                )
                
                # 添加标题
                story.append(Paragraph(filename, title_style))
                story.append(Spacer(1, 20))
                
                # 添加段落内容
                for paragraph in doc.paragraphs:
                    if paragraph.text.strip():
                        # 转义特殊字符
                        text = paragraph.text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                        try:
                            p = Paragraph(text, chinese_style)
                            story.append(p)
                            story.append(Spacer(1, 12))
                        except Exception as e:
                            # 如果某个段落出错，跳过
                            print(f"    警告: 段落处理失败，已跳过")
                            continue
                
                # 生成PDF
                pdf_doc.build(story)
                converted_files.append(pdf_path)
                print(f"  ✓ 转换成功: {os.path.basename(pdf_path)}")
                
            except Exception as e:
                print(f"  ✗ 转换失败: {str(e)}")
                continue
        
        print(f"\n预处理完成！成功转换 {len(converted_files)} 个文档")
        print("=" * 50 + "\n")
        return converted_files
    
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
                    
                    # 检查图片方向：如果宽度大于高度（横向），则旋转90度使其竖向
                    width, height = img.size
                    if width > height:
                        print(f"检测到横向图片 {os.path.basename(filepath)} ({width}x{height})，旋转90度...")
                        img = img.rotate(270, expand=True)
                    else:
                        print(f"图片 {os.path.basename(filepath)} 已是竖向 ({width}x{height})，无需旋转")
                    
                    if img.mode in ('RGBA', 'LA', 'P'):
                        img = img.convert('RGB')
                    
                    # 保存到临时文件后再转换为PDF
                    temp_img_path = output_pdf.replace('.pdf', '_temp.jpg')
                    img.save(temp_img_path, 'JPEG', quality=95)
                    
                    # 转换为PDF
                    pdf_bytes = img2pdf.convert(temp_img_path)
                    f.write(pdf_bytes)
                    
                    # 删除临时图片
                    if os.path.exists(temp_img_path):
                        os.remove(temp_img_path)
                return True
            elif ext in ['.doc', '.docx']:
                if is_windows:
                    try:
                        from docx2pdf import convert
                        print(f"  [Windows] 使用docx2pdf转换Word文档...")
                        convert(filepath, output_pdf)
                        if os.path.exists(output_pdf):
                            print(f"  ✓ Word转PDF成功")
                            return True
                        else:
                            print(f"  ✗ 转换失败: PDF文件未生成")
                            return False
                    except Exception as e:
                        print(f"  ✗ Word转PDF失败: {str(e)}")
                        print(f"  提示: 请确保已安装Microsoft Word，docx2pdf需要Word才能工作")
                        return False
                else:
                    # macOS/Linux: 使用LibreOffice
                    print(f"  [macOS/Linux] 使用LibreOffice转换Word文档...")
                    try:
                        result = subprocess.run(
                            ['soffice', '--headless', '--convert-to', 'pdf', '--outdir',
                             os.path.dirname(output_pdf), filepath],
                            capture_output=True, timeout=30, text=True
                        )
                        expected_pdf = os.path.join(
                            os.path.dirname(output_pdf),
                            os.path.splitext(os.path.basename(filepath))[0] + '.pdf'
                        )
                        if os.path.exists(expected_pdf):
                            if expected_pdf != output_pdf:
                                shutil.move(expected_pdf, output_pdf)
                            print(f"  ✓ Word转PDF成功")
                            return True
                        else:
                            print(f"  ✗ 转换失败: PDF文件未生成")
                            if result.stderr:
                                print(f"  错误信息: {result.stderr}")
                            print(f"  提示: 请安装LibreOffice: brew install --cask libreoffice")
                            return False
                    except FileNotFoundError:
                        print(f"  ✗ 找不到soffice命令")
                        print(f"  提示: 请安装LibreOffice: brew install --cask libreoffice")
                        return False
                    except subprocess.TimeoutExpired:
                        print(f"  ✗ 转换超时(30秒)")
                        return False
                    except Exception as e:
                        print(f"  ✗ Word转PDF失败: {str(e)}")
                        return False
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
        pdf_temp_dir = None
        try:
            if not os.path.isdir(folder_path):
                raise Exception("选择的路径不是有效的文件夹")
            
            # 新增：预处理Word文档（.doc和.docx）
            if progress_callback:
                progress_callback(5, "预处理Word文档...")
            
            self.preprocess_word_files(folder_path, progress_callback)
            
            if progress_callback:
                progress_callback(20, "正在扫描文件...")
            
            all_files = self.find_files(folder_path)
            print(f"找到 {len(all_files)} 个文件")
            
            if not all_files:
                raise Exception("文件夹中没有找到任何文件")
            
            classified = self.sort_files(all_files)
            
            # 打印分类结果用于调试
            for doc_type, files in classified.items():
                if files:
                    print(f"{doc_type}: {len(files)} 个文件")
            
            if progress_callback:
                progress_callback(40, "正在转换文档...")
            
            pdf_temp_dir = tempfile.mkdtemp(prefix='pdf_temp_')
            ordered_pdfs = []
            
            order = [
                '申请书', '户主声明书', '承包方调查表', '承包地块调查表',
                '公示结果归户表', '公示无异议声明书', '土地承包合同书',
                '登记簿', '地块示意图', '确权登记声明书', '承诺书'
            ]
            
            total_files = sum(len(classified[t]) for t in order)
            if total_files == 0:
                raise Exception("没有找到可识别的文档类型，请检查文件名是否包含正确的关键字")
            
            processed = 0
            
            for doc_type in order:
                files = classified[doc_type]
                for i, filepath in enumerate(files):
                    print(f"正在处理: {os.path.basename(filepath)}")
                    repeat_count = 4 if doc_type == '土地承包合同书' else 1
                    for repeat in range(repeat_count):
                        output_name = f"{len(ordered_pdfs):03d}_{doc_type}_{i}_{repeat}.pdf"
                        output = os.path.join(pdf_temp_dir, output_name)
                        try:
                            if self.convert_to_pdf(filepath, output):
                                ordered_pdfs.append(output)
                                print(f"  ✓ 转换成功")
                            else:
                                print(f"  ✗ 转换失败")
                        except Exception as e:
                            print(f"  ✗ 转换出错: {str(e)}")
                    processed += 1
                    if progress_callback and total_files > 0:
                        progress = 40 + int((processed / total_files) * 45)
                        progress_callback(progress, f"正在处理: {doc_type}... ({processed}/{total_files})")
            
            if not ordered_pdfs:
                raise Exception("没有成功转换任何文档，请检查文件格式是否支持")
            
            print(f"共转换 {len(ordered_pdfs)} 个PDF页面")
            
            if progress_callback:
                progress_callback(90, "正在合并PDF...")
            
            self.merge_pdfs(ordered_pdfs, output_pdf)
            print(f"PDF已合并: {output_pdf}")
            
            if pdf_temp_dir and os.path.exists(pdf_temp_dir):
                shutil.rmtree(pdf_temp_dir, ignore_errors=True)
            
            if progress_callback:
                progress_callback(100, "完成！")
            
            return True
        except Exception as e:
            # 清理临时文件
            if pdf_temp_dir and os.path.exists(pdf_temp_dir):
                shutil.rmtree(pdf_temp_dir, ignore_errors=True)
            print(f"处理出错: {str(e)}")
            raise e


class SimpleGUI:
    """简洁的图形界面"""
    
    def __init__(self):
        # 首先检查设备绑定（不计数）
        self.license_manager = LicenseManager()
        can_use, message = self.license_manager.check_device()
        
        if not can_use:
            # 创建临时窗口显示错误
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "程序已损坏", 
                f"抱歉，程序文件已损坏，无法继续使用。\n\n错误信息: {message}\n\n请联系技术支持获取新版本。"
            )
            root.destroy()
            exit(1)
        
        self.root = tk.Tk()
        self.root.title("文档处理器")
        self.root.geometry("600x600")  # 增加高度以容纳授权信息
        
        # 强制设置背景色
        self.root.configure(bg='#e8e8e8')
        
        self.processor = DocumentProcessor()
        self.selected_folder = None
        self.output_pdf_path = None
        
        # 检测Word转换器
        self.word_available, self.word_message = DocumentProcessor.check_word_converter()
        
        self.create_widgets()
        self.center_window()
        
        # 显示授权信息（启动时不显示警告）
        # self.show_license_info(message)
        
        # 如果Word/LibreOffice不可用，显示警告
        if not self.word_available:
            self.show_word_warning()
    
    def show_word_warning(self):
        """显示Word转换器不可用的警告"""
        # 不立即弹窗，而是在界面上显示警告信息
        # 用户可以选择继续（如果没有Word文档）或退出安装
        pass  # 警告信息已在界面中显示
    
    def show_license_info(self, message):
        """显示授权信息的提示框"""
        # 如果剩余次数少于20次，显示警告
        usage_info = self.license_manager.get_usage_info()
        if ":" in usage_info:
            remaining_str = usage_info.split(":")[1].strip().split(" ")[0]
            try:
                remaining = int(remaining_str)
                if remaining <= 20:
                    messagebox.showwarning(
                        "",
                        f"提示：已损坏{usage_info}\n\n请注意！"
                    )
            except:
                pass
    
    def update_license_display(self):
        """更新界面上的授权信息显示"""
        try:
            usage_info = self.license_manager.get_usage_info()
            if hasattr(self, 'license_label'):
                self.license_label.config(text=f"📋 {usage_info}")
                self.root.update()
            print(f"[界面更新] {usage_info}")
        except Exception as e:
            print(f"更新界面显示失败: {e}")
    
    def center_window(self):
        """窗口居中"""
        self.root.update_idletasks()
        width = 600
        height = 600
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
        
        # 授权信息
        license_frame = tk.Frame(self.root, bg='#e8e8e8')
        license_frame.pack(fill=tk.X, padx=20, pady=(0, 5))
        
        usage_info = self.license_manager.get_usage_info()
        self.license_label = tk.Label(
            license_frame,
            text=f"📋 {usage_info}",
            font=("Arial", 9),
            bg='#e8e8e8',
            fg='#7f8c8d'
        )
        self.license_label.pack(anchor=tk.E)
        
        # Word转换器状态提示
        status_frame = tk.Frame(self.root, bg='#e8e8e8')
        status_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        if self.word_available:
            status_text = self.word_message
            status_color = '#27ae60'  # 绿色
        else:
            status_text = self.word_message.split('\n')[0]  # 只显示第一行
            status_color = '#e67e22'  # 橙色
        
        status_label = tk.Label(
            status_frame,
            text=status_text,
            font=("Arial", 10),
            bg='#e8e8e8',
            fg=status_color,
            wraplength=550,
            justify=tk.LEFT
        )
        status_label.pack(anchor=tk.W)
        
        # 如果Word不可用，显示详细说明按钮
        if not self.word_available:
            help_btn = tk.Button(
                status_frame,
                text="查看详细说明",
                command=self.show_word_help,
                bg='#3498db',
                fg='white',
                font=("Arial", 9),
                cursor='hand2',
                relief=tk.FLAT,
                padx=10,
                pady=2
            )
            help_btn.pack(anchor=tk.W, pady=(5, 0))
        
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
            text="步骤 2：开始处理",
            font=("Arial", 12, "bold"),
            bg='white',
            fg='#34495e',
            padx=20,
            pady=15
        )
        frame2.pack(fill=tk.X, padx=20, pady=10)
        
        hint_label = tk.Label(
            frame2,
            text="点击后会让您选择保存位置，然后自动处理文档",
            font=("Arial", 9),
            bg='white',
            fg='#7f8c8d'
        )
        hint_label.pack(pady=(0, 10))
        
        self.process_btn = tk.Button(
            frame2,
            text="🚀 开始处理并保存",
            command=self.process,
            font=("Arial", 12, "bold"),
            bg='#2ecc71',
            fg='white',
            padx=30,
            pady=10,
            state='disabled'
        )
        self.process_btn.pack(pady=5)
        
        self.progress_label = tk.Label(
            frame2,
            text="等待选择文件夹...",
            font=("Arial", 10),
            bg='white',
            fg='#7f8c8d'
        )
        self.progress_label.pack(pady=10)
    
    def show_word_help(self):
        """显示Word转换器帮助信息"""
        messagebox.showinfo(
            "Word转换器说明",
            self.word_message + "\n\n如果文件夹中没有.docx文件，\n可以直接继续使用。\n\nPDF和图片文件不受影响。"
        )
    
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
        try:
            self.progress_label.config(text=message)
            self.root.update()
        except:
            # 如果UI组件失效，只打印到控制台
            print(f"[{value}%] {message}")
    
    def process(self):
        """处理文档"""
        print("=" * 50)
        print("开始处理按钮被点击")
        
        if not self.selected_folder:
            print("错误: 未选择文件夹")
            messagebox.showerror("错误", "请先选择文件夹")
            return
        
        # 检查并更新使用次数
        can_use, usage_message = self.license_manager.check_and_update_usage()
        if not can_use:
            messagebox.showerror(
                "程序已损坏",
                f"抱歉，程序文件已损坏，无法继续使用。\n\n错误信息: {usage_message}\n\n请联系技术支持获取新版本。"
            )
            return
        
        # 更新界面显示的使用次数
        self.update_license_display()
        
        # 如果剩余次数少于20次，显示警告
        usage_info = self.license_manager.get_usage_info()
        if "剩余:" in usage_info or "，:" in usage_info:
            try:
                # 提取剩余次数
                parts = usage_info.split("，:")
                if len(parts) > 1:
                    remaining_str = parts[1].strip().split(" ")[0]
                    remaining = int(remaining_str)
                    if remaining <= 20:
                        messagebox.showwarning(
                            "使用次数提醒",
                            f"提示：{usage_info}\n\n即将达到使用上限，请注意！"
                        )
            except:
                pass
        
        print(f"选择的文件夹: {self.selected_folder}")
        print(f"使用次数信息: {usage_message}")
        
        # 先让用户选择保存位置
        folder_name = os.path.basename(self.selected_folder)
        save_path = filedialog.asksaveasfilename(
            title="选择PDF保存位置",
            defaultextension=".pdf",
            initialfile=f"{folder_name}_合并.pdf",
            filetypes=[("PDF文件", "*.pdf")]
        )
        
        if not save_path:
            print("用户取消了保存")
            return
        
        print(f"保存路径: {save_path}")
        
        # 禁用按钮
        self.process_btn.config(state='disabled')
        self.progress_label.config(text="正在准备处理...", fg='black')
        self.root.update()  # 强制刷新界面
        
        try:
            print("开始调用 process_folder...")
            self.processor.process_folder(
                self.selected_folder,
                save_path,
                progress_callback=self.update_progress
            )
            
            print(f"处理完成，检查输出文件: {os.path.exists(save_path)}")
            
            try:
                self.progress_label.config(text="✅ 处理完成！", fg='#27ae60')
                # 再次更新使用次数显示（确保显示最新状态）
                self.update_license_display()
                self.root.update()
            except:
                pass
            
            # 询问是否打开文件夹
            result = messagebox.askyesno(
                "成功", 
                f"文档处理完成！\n\nPDF已保存到:\n{save_path}\n\n是否打开文件所在文件夹？"
            )
            
            if result:
                import platform
                folder = os.path.dirname(save_path)
                if platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', folder])
                elif platform.system() == 'Windows':
                    os.startfile(folder)
            
        except Exception as e:
            print(f"处理失败: {str(e)}")
            import traceback
            traceback.print_exc()
            
            messagebox.showerror("错误", f"处理失败:\n\n{str(e)}")
            try:
                self.progress_label.config(text=f"❌ 错误: {str(e)}", fg='red')
            except:
                pass
            
        finally:
            try:
                self.process_btn.config(state='normal')
                self.root.update()
            except:
                pass
            print("处理流程结束")
            print("=" * 50)
    
    def run(self):
        """运行程序"""
        self.root.mainloop()


if __name__ == "__main__":
    print("正在启动文档处理器...")
    app = SimpleGUI()
    app.run()
