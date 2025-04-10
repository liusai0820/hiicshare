#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from bs4 import BeautifulSoup
import argparse

def split_html_slides(input_file, output_dir=None):
    """
    将包含多个幻灯片的HTML文件拆分为多个单页HTML文件
    
    参数:
        input_file: 输入的HTML文件路径
        output_dir: 可选输出目录，如果不提供则使用与输入文件相同的目录
    
    返回:
        生成的文件列表
    """
    print(f"正在处理文件: {input_file}")
    
    # 获取输入文件名和扩展名
    file_path, file_ext = os.path.splitext(input_file)
    base_name = os.path.basename(file_path)
    
    # 如果没有指定输出目录，则使用输入文件所在的目录
    if output_dir is None:
        output_dir = os.path.dirname(input_file)
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 读取HTML文件内容
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        print(f"成功读取文件，大小: {len(html_content)} 字节")
    except Exception as e:
        print(f"读取文件 {input_file} 时出错: {str(e)}")
        return []
    
    # 直接用正则表达式提取幻灯片部分，避免嵌套问题
    slide_pattern = r'<div\s+class="slide-container".*?>\s*?<div\s+class="header".*?>.*?</div>\s*?<div\s+class="content-area".*?>.*?</div>\s*?<div\s+class="footer".*?>.*?</div>\s*?</div>'
    slide_matches = re.findall(slide_pattern, html_content, re.DOTALL)
    
    if not slide_matches:
        print(f"警告: 在文件 {input_file} 中没有找到完整的幻灯片。尝试其他匹配方式...")
        
        # 尝试一种更宽松的匹配模式
        slide_pattern = r'<div\s+class="slide-container".*?>.*?<div\s+class="footer".*?>.*?</div>\s*?</div>'
        slide_matches = re.findall(slide_pattern, html_content, re.DOTALL)
        
    print(f"找到 {len(slide_matches)} 个幻灯片")
    
    if not slide_matches:
        print(f"错误: 无法在文件 {input_file} 中找到幻灯片。")
        return []
    
    # 提取头部信息（样式、脚本等）
    head_match = re.search(r'<head>.*?</head>', html_content, re.DOTALL)
    head_content = head_match.group(0) if head_match else "<head><title>幻灯片</title></head>"
    
    # 处理每个幻灯片
    created_files = []
    
    for i, slide_html in enumerate(slide_matches, 1):
        print(f"处理第 {i} 个幻灯片...")
        
        # 创建新的完整HTML文档
        new_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
{head_content}
<body>
{slide_html}
</body>
</html>"""
        
        # 生成输出文件名
        output_file = os.path.join(output_dir, f"{base_name}{i}{file_ext}")
        
        # 将生成的HTML写入新文件
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(new_html)
            created_files.append(output_file)
            print(f"已创建: {output_file}")
        except Exception as e:
            print(f"创建文件 {output_file} 时出错: {str(e)}")
    
    print(f"已成功将 {input_file} 拆分为 {len(created_files)} 个单页文件")
    return created_files

def main():
    parser = argparse.ArgumentParser(description='将多页HTML演示文稿拆分为单页文件')
    parser.add_argument('files', nargs='*', help='要处理的HTML文件列表')
    parser.add_argument('-o', '--output-dir', help='输出目录')
    parser.add_argument('--all', action='store_true', help='处理html-ppt目录中的2-lobe.html, 3-chain.html, 4-aislide.html, 5-xie.html')
    
    args = parser.parse_args()
    
    if args.all:
        print("正在处理所有指定的HTML文件...")
        html_dir = 'html-ppt'
        target_files = ['2-lobe.html', '3-chain.html', '4-aislide.html', '5-xie.html']
        for file_name in target_files:
            file_path = os.path.join(html_dir, file_name)
            if os.path.exists(file_path):
                split_html_slides(file_path, args.output_dir)
            else:
                print(f"文件不存在: {file_path}")
    elif args.files:
        for file_path in args.files:
            if os.path.exists(file_path):
                split_html_slides(file_path, args.output_dir)
            else:
                print(f"文件不存在: {file_path}")
    else:
        parser.print_help()
        print("\n错误: 请指定要处理的文件或使用--all选项")

if __name__ == "__main__":
    main() 