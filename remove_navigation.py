import os
import glob
import re
from bs4 import BeautifulSoup

# 配置
html_dir = 'html-ppt'  # HTML文件所在的目录

def remove_navigation():
    """移除HTML文件中的导航元素"""
    html_files = glob.glob(os.path.join(html_dir, '*.html'))
    if not html_files:
        print(f"错误：在 '{html_dir}' 目录下没有找到任何 .html 文件。")
        return

    print(f"找到 {len(html_files)} 个 HTML 文件。开始处理...")

    for filepath in html_files:
        print(f"  正在处理: {filepath}")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(content, 'html.parser')
            
            # 1. 移除全屏导航元素
            fs_nav = soup.find(id='fs-nav')
            if fs_nav:
                fs_nav.decompose()
                print(f"    - 移除了全屏导航元素")
            
            # 2. 移除全屏按钮
            fs_btn = soup.find(id='fs-btn')
            if fs_btn:
                fs_btn.decompose()
                print(f"    - 移除了全屏按钮")
            
            # 3. 移除与导航相关的JavaScript代码
            # 找到所有script标签
            scripts = soup.find_all('script')
            for script in scripts:
                # 如果script标签有内容并且包含导航相关代码
                if script.string and any(term in script.string for term in ['fs-nav', 'fs-btn', 'fs-prev-btn', 'fs-next-btn']):
                    script.decompose()
                    print(f"    - 移除了导航相关的JavaScript代码")
            
            # 4. 保留页脚信息，但删除页码/导航按钮
            # 修改footer区域，保留左侧文本，删除右侧页码
            footer = soup.find(class_='footer')
            if footer:
                # 查找页码元素
                page_number = footer.find(class_='page-number')
                if page_number:
                    page_number.decompose()
                    print(f"    - 从页脚移除了页码显示")
            
            # 将修改后的内容写回文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            print(f"    ✅ 成功更新文件")
        
        except Exception as e:
            print(f"    ! 错误: 处理 {filepath} 时发生错误: {e}")

    print("处理完成。所有导航元素已移除。")

if __name__ == "__main__":
    remove_navigation() 