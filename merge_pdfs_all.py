import os
import glob
from PyPDF2 import PdfMerger

# 配置
pdf_dir = 'pdf-output'  # PDF文件所在的目录
merged_output = 'all_slides.pdf'  # 合并后的PDF文件名

def merge_pdfs():
    """合并目录中的所有PDF文件为一个文件"""
    try:
        # 获取所有PDF文件并按文件名排序
        pdf_files = sorted(
            [f for f in glob.glob(f"{pdf_dir}/*.pdf") if os.path.basename(f) != merged_output],
            key=lambda x: int(os.path.basename(x).split('-')[0]) if os.path.basename(x).split('-')[0].isdigit() else 999
        )
        
        if not pdf_files:
            print("没有找到要合并的PDF文件")
            return
        
        print(f"开始合并 {len(pdf_files)} 个PDF文件...")
        
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