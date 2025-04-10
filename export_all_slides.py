import os
import glob
import asyncio
from pyppeteer import launch
from PyPDF2 import PdfMerger

# 配置
html_dir = 'html-ppt'  # HTML文件所在的目录
output_dir = 'pdf-output'  # 输出PDF的目录
merged_output = 'presentation.pdf'  # 合并后的PDF文件名
width = 1280  # 导出宽度
height = 720  # 导出高度

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

# 查找本地 Chrome 浏览器路径
def find_chrome():
    # MacOS上的常见Chrome路径
    possible_paths = [
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary',
        '/Applications/Chromium.app/Contents/MacOS/Chromium',
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # 尝试用 which 命令查找
    try:
        import subprocess
        result = subprocess.run(['which', 'google-chrome'], capture_output=True, text=True)
        if result.stdout.strip():
            return result.stdout.strip()
    except:
        pass
    
    return None

async def export_all_slides():
    # 查找Chrome路径
    chrome_path = find_chrome()
    if not chrome_path:
        print("❌ 无法找到本地Chrome浏览器，请确认它已安装。")
        return
    
    print(f"✅ 找到Chrome浏览器: {chrome_path}")
    
    # 启动浏览器
    browser = await launch(
        headless=True,  # 无头模式
        executablePath=chrome_path,
        args=[
            '--no-sandbox', 
            '--disable-setuid-sandbox', 
            '--disable-dev-shm-usage',
            '--allow-file-access-from-files',  # 允许从文件加载资源
        ]
    )
    
    # 获取所有HTML文件并按文件名排序
    html_files = sorted([f for f in os.listdir(html_dir) if f.endswith('.html')], 
                       key=lambda x: int(x.split('-')[0]) if x.split('-')[0].isdigit() else 999)
    
    print(f"找到 {len(html_files)} 个HTML文件")
    
    all_pdf_files = []  # 存储所有生成的PDF文件路径
    
    for html_file in html_files:
        file_path = os.path.join(html_dir, html_file)
        base_name = os.path.splitext(html_file)[0]
        
        print(f"处理: {html_file}")
        
        # 创建页面
        page = await browser.newPage()
        await page.setViewport({'width': width, 'height': height})
        
        # 访问本地文件
        file_url = f"file://{os.path.abspath(file_path)}"
        await page.goto(file_url, {'waitUntil': 'networkidle0', 'timeout': 60000})
        
        # 等待加载
        await asyncio.sleep(2)
        
        # 检查页面内是否有多页内容 (查找页码指示器)
        has_multiple_pages = await page.evaluate('''() => {
            // 检查是否存在可能表示多页的元素
            const pageIndicators = document.querySelectorAll('.page-number');
            for (let indicator of pageIndicators) {
                const text = indicator.textContent.trim();
                // 查找类似 "1/3" 格式的页码
                if (text.includes('/')) {
                    return true;
                }
            }
            
            // 检查是否存在导航按钮可能表示多页
            const nextButtons = document.querySelectorAll('button[id$="-next"], .next-btn, .next');
            return nextButtons.length > 0;
        }''')
        
        if has_multiple_pages:
            print(f"  检测到多页内容")
            
            # 获取总页数
            total_pages = await page.evaluate('''() => {
                // 尝试从页码指示器获取总页数
                const pageIndicators = document.querySelectorAll('.page-number');
                for (let indicator of pageIndicators) {
                    const text = indicator.textContent.trim();
                    if (text.includes('/')) {
                        const parts = text.split('/');
                        if (parts.length >= 2) {
                            return parseInt(parts[1], 10) || 3; // 默认假设有3页
                        }
                    }
                }
                return 3; // 默认假设有3页
            }''')
            
            print(f"  估计总页数: {total_pages}")
            
            # 在导出前移除导航元素
            await page.evaluate('''() => {
                // 移除所有可能的导航元素
                const elementsToRemove = document.querySelectorAll('.controls, .nav-controls, .pagination, #fs-nav, #fs-btn');
                elementsToRemove.forEach(el => {
                    if(el) el.remove();
                });
                
                // 可能的页码/导航元素类名
                const navClassNames = ['page-number', 'page-indicator', 'navigation', 'controls', 'page-controls'];
                navClassNames.forEach(className => {
                    const elements = document.querySelectorAll('.' + className);
                    elements.forEach(el => {
                        if(el) el.remove();
                    });
                });
            }''')
            
            # 为每一页创建PDF
            for page_num in range(1, total_pages + 1):
                # 生成PDF文件名，包含子页码
                pdf_filename = f"{base_name}-{page_num}.pdf"
                pdf_path = os.path.join(output_dir, pdf_filename)
                
                # 在导出前切换到指定页面
                if page_num > 1:
                    # 寻找并点击"下一页"按钮
                    await page.evaluate('''() => {
                        // 尝试点击下一页按钮
                        const nextButtons = document.querySelectorAll('button[id$="-next"], .next-btn, .next');
                        if (nextButtons.length > 0) {
                            nextButtons[0].click();
                        }
                    }''')
                    await asyncio.sleep(1)  # 等待页面切换
                
                # 导出当前页面为PDF
                await page.pdf({
                    'path': pdf_path,
                    'width': f"{width}px",
                    'height': f"{height}px",
                    'printBackground': True,
                    'margin': {'top': 0, 'right': 0, 'bottom': 0, 'left': 0}
                })
                
                print(f"  ✅ 导出第 {page_num} 页: {pdf_path}")
                all_pdf_files.append(pdf_path)
        else:
            # 单页内容，直接导出
            pdf_filename = f"{base_name}.pdf"
            pdf_path = os.path.join(output_dir, pdf_filename)
            
            # 在导出前移除导航元素
            await page.evaluate('''() => {
                // 移除所有可能的导航元素
                const elementsToRemove = document.querySelectorAll('.controls, .nav-controls, .pagination, #fs-nav, #fs-btn');
                elementsToRemove.forEach(el => {
                    if(el) el.remove();
                });
                
                // 可能的页码/导航元素类名
                const navClassNames = ['page-number', 'page-indicator', 'navigation', 'controls', 'page-controls'];
                navClassNames.forEach(className => {
                    const elements = document.querySelectorAll('.' + className);
                    elements.forEach(el => {
                        if(el) el.remove();
                    });
                });
            }''')
            
            # 导出PDF
            await page.pdf({
                'path': pdf_path,
                'width': f"{width}px",
                'height': f"{height}px",
                'printBackground': True,
                'margin': {'top': 0, 'right': 0, 'bottom': 0, 'left': 0}
            })
            
            print(f"  ✅ 导出单页: {pdf_path}")
            all_pdf_files.append(pdf_path)
        
        # 关闭页面
        await page.close()
    
    # 关闭浏览器
    await browser.close()
    print("所有PDF导出完成!")
    
    # 合并所有PDF
    merge_pdfs(all_pdf_files, os.path.join(output_dir, merged_output))

def merge_pdfs(pdf_files, output_path):
    """合并PDF文件列表为一个文件"""
    try:
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
        merger.write(output_path)
        merger.close()
        
        print(f"✅ 所有PDF已合并为: {output_path}")
    except Exception as e:
        print(f"❌ 合并PDF时出错: {e}")

# 运行异步函数
if __name__ == "__main__":
    asyncio.run(export_all_slides()) 