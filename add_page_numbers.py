import os
import re
from bs4 import BeautifulSoup
import glob

# HTML文件所在的目录
html_dir = 'html-ppt'

def extract_number_prefix(filename):
    """从文件名中提取数字前缀"""
    match = re.match(r'(\d+)', os.path.basename(filename))
    if match:
        return int(match.group(1))
    return 999  # 如果没有数字前缀，则排在后面

def add_page_numbers():
    """为所有HTML幻灯片添加页码"""
    # 获取所有HTML文件并按数字前缀排序
    html_files = glob.glob(f"{html_dir}/*.html")
    html_files.sort(key=extract_number_prefix)
    
    total_files = len(html_files)
    print(f"找到 {total_files} 个HTML文件，开始添加页码...")
    
    for index, file_path in enumerate(html_files, start=1):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file.read(), 'html.parser')
            
            # 找到footer元素
            footer = soup.select_one('.footer')
            if not footer:
                print(f"警告: 在 {os.path.basename(file_path)} 中没有找到footer元素，跳过")
                continue
            
            # 清除footer的内容并创建新的结构
            footer.clear()
            
            # 添加左侧内容
            left_div = soup.new_tag('div')
            left_div.string = 'AI赋能工作效率提升实践分享'
            footer.append(left_div)
            
            # 添加右侧页码
            page_number = soup.new_tag('div')
            page_number['class'] = 'page-number'
            page_number.string = f'{index}/{total_files}'
            footer.append(page_number)
            
            # 确保footer是可见的（移除display:none）
            if 'style' in footer.attrs and 'display: none' in footer['style']:
                del footer['style']
            
            # 保存修改后的文件
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(str(soup))
            
            print(f"✅ 已为 {os.path.basename(file_path)} 添加页码 {index}/{total_files}")
            
        except Exception as e:
            print(f"❌ 处理 {os.path.basename(file_path)} 时出错: {e}")
    
    print(f"✅ 已完成所有{total_files}个文件的页码添加")

if __name__ == "__main__":
    add_page_numbers() 