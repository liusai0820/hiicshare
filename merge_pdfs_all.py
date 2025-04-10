import os
import glob
import re
from PyPDF2 import PdfMerger

# 配置
pdf_dir = 'pdf-output'  # PDF文件所在的目录
merged_output = 'all_slides.pdf'  # 合并后的PDF文件名

def sort_key(filename):
    """为文件名创建排序键，考虑主数字和次数字"""
    basename = os.path.basename(filename)
    # 使用正则表达式提取所有数字部分
    numbers = re.findall(r'\d+', basename)
    
    if not numbers:
        return (999, 999)  # 如果没有数字，则放在最后
    
    # 第一个数字作为主排序键
    primary = int(numbers[0])
    
    # 如果有第二个数字，则作为次排序键，否则默认为0
    secondary = int(numbers[1]) if len(numbers) > 1 else 0
    
    return (primary, secondary)

def merge_pdfs():
    """合并目录中的所有PDF文件为一个文件"""
    try:
        # 获取所有PDF文件并按文件名排序
        pdf_files = sorted(
            [f for f in glob.glob(f"{pdf_dir}/*.pdf") if os.path.basename(f) != merged_output],
            key=sort_key
        )
        
        if not pdf_files:
            print("没有找到要合并的PDF文件")
            return
        
        print(f"开始合并 {len(pdf_files)} 个PDF文件...")
        print("文件排序如下:")
        for i, pdf in enumerate(pdf_files):
            print(f"  {i+1}. {os.path.basename(pdf)}")
        
        # 创建PDF合并器
        merger = PdfMerger()
        
        # 添加每个PDF文件
        for pdf in pdf_files:
            try:
                merger.append(pdf)
                print(f"  已添加: {os.path.basename(pdf)}")
            except Exception as e:
                print(f"  ❌ 无法添加 {os.path.basename(pdf)}: {e}")
        
        # 写入合并后的PDF
        output_path = os.path.join(pdf_dir, merged_output)
        merger.write(output_path)
        merger.close()
        
        print(f"✅ 所有PDF已合并为: {output_path}")
        print(f"  文件大小: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")
    except Exception as e:
        print(f"❌ 合并PDF时出错: {e}")

if __name__ == "__main__":
    merge_pdfs() 