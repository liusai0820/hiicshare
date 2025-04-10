#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from bs4 import BeautifulSoup
import argparse

def remove_page_numbers(input_file, output_file=None):
    """
    从HTML文件中移除页码相关代码
    
    参数:
        input_file: 输入的HTML文件路径
        output_file: 输出的HTML文件路径，如果不提供则覆盖原文件
    
    返回:
        是否成功移除页码
    """
    print(f"正在处理文件: {input_file}")
    
    # 如果没有指定输出文件，则覆盖原文件
    if output_file is None:
        output_file = input_file
    
    # 读取HTML文件内容
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        print(f"成功读取文件，大小: {len(html_content)} 字节")
    except Exception as e:
        print(f"读取文件 {input_file} 时出错: {str(e)}")
        return False
    
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 找到并移除页码相关元素
    page_numbers = soup.find_all('div', class_='page-number')
    if page_numbers:
        print(f"找到 {len(page_numbers)} 个页码元素")
        for page_number in page_numbers:
            page_number.extract()  # 从DOM中移除这个元素
    else:
        print(f"在文件 {input_file} 中没有找到页码元素")
    
    # 找到并移除页面控制元素
    page_controls = soup.find_all('div', class_='page-controls')
    if page_controls:
        print(f"找到 {len(page_controls)} 个页面控制元素")
        for page_control in page_controls:
            page_control.extract()  # 从DOM中移除这个元素
    
    # 找到并移除所有onclick="prevSlide()"和onclick="nextSlide()"的按钮
    nav_buttons = soup.find_all(onclick=re.compile(r'(prevSlide|nextSlide)\(\)'))
    if nav_buttons:
        print(f"找到 {len(nav_buttons)} 个导航按钮")
        for button in nav_buttons:
            button.extract()  # 从DOM中移除这个元素
    
    # 找到包含当前页码和总页数的span元素
    page_spans = soup.find_all('span', class_=['current-page', 'total-pages'])
    if page_spans:
        print(f"找到 {len(page_spans)} 个页码span元素")
        for span in page_spans:
            span.extract()  # 从DOM中移除这个元素
    
    # 移除页码相关的JavaScript函数
    scripts = soup.find_all('script')
    for script in scripts:
        if script.string and ('nextSlide' in script.string or 'prevSlide' in script.string or 'updatePagination' in script.string):
            print("找到并移除页码相关脚本")
            script.extract()  # 从DOM中移除这个脚本
    
    # 将修改后的HTML写入输出文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        print(f"已保存修改后的文件: {output_file}")
        return True
    except Exception as e:
        print(f"保存文件 {output_file} 时出错: {str(e)}")
        return False

def process_directory(directory, output_dir=None):
    """
    处理目录中的所有HTML文件
    
    参数:
        directory: 输入目录路径
        output_dir: 输出目录路径，如果不提供则覆盖原文件
    
    返回:
        成功处理的文件数量
    """
    if not os.path.isdir(directory):
        print(f"错误: {directory} 不是一个有效的目录")
        return 0
    
    # 如果指定了输出目录，确保它存在
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    success_count = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                input_file = os.path.join(root, file)
                
                # 确定输出文件路径
                if output_dir:
                    # 保持相对目录结构
                    rel_path = os.path.relpath(root, directory)
                    output_subdir = os.path.join(output_dir, rel_path)
                    os.makedirs(output_subdir, exist_ok=True)
                    output_file = os.path.join(output_subdir, file)
                else:
                    output_file = None  # 覆盖原文件
                
                # 处理文件
                if remove_page_numbers(input_file, output_file):
                    success_count += 1
    
    return success_count

def main():
    parser = argparse.ArgumentParser(description='从HTML文件中移除页码相关代码')
    parser.add_argument('files', nargs='*', help='要处理的HTML文件或目录列表')
    parser.add_argument('-o', '--output-dir', help='输出目录，如果处理单个文件则为输出文件')
    parser.add_argument('--all', action='store_true', help='处理指定目录中的所有HTML文件')
    parser.add_argument('-d', '--directory', help='要处理的目录')
    
    args = parser.parse_args()
    
    if args.all and args.directory:
        print(f"正在处理目录 {args.directory} 中的所有HTML文件...")
        count = process_directory(args.directory, args.output_dir)
        print(f"成功处理了 {count} 个文件")
    elif args.all:
        directory = 'html-ppt'
        print(f"正在处理目录 {directory} 中的所有HTML文件...")
        count = process_directory(directory, args.output_dir)
        print(f"成功处理了 {count} 个文件")
    elif args.files:
        for file_path in args.files:
            if os.path.isdir(file_path):
                print(f"正在处理目录 {file_path} 中的所有HTML文件...")
                count = process_directory(file_path, args.output_dir)
                print(f"成功处理了 {count} 个文件")
            elif os.path.exists(file_path):
                # 如果是处理单个文件，并且指定了输出目录
                if args.output_dir:
                    if os.path.isdir(args.output_dir):
                        output_file = os.path.join(args.output_dir, os.path.basename(file_path))
                    else:
                        output_file = args.output_dir
                else:
                    output_file = None  # 覆盖原文件
                
                remove_page_numbers(file_path, output_file)
            else:
                print(f"文件不存在: {file_path}")
    else:
        parser.print_help()
        print("\n错误: 请指定要处理的文件或目录，或使用--all选项")

if __name__ == "__main__":
    main() 