import asyncio
import os
from pyppeteer import launch
import time
import glob
from PyPDF2 import PdfMerger
import subprocess

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
        result = subprocess.run(['which', 'google-chrome'], capture_output=True, text=True)
        if result.stdout.strip():
            return result.stdout.strip()
    except:
        pass
    
    try:
        result = subprocess.run(['which', 'chrome'], capture_output=True, text=True)
        if result.stdout.strip():
            return result.stdout.strip()
    except:
        pass
    
    return None

async def export_to_pdf():
    # 查找Chrome路径
    chrome_path = find_chrome()
    if not chrome_path:
        print("❌ 无法找到本地Chrome浏览器，请确认它已安装。")
        return
    
    print(f"✅ 找到Chrome浏览器: {chrome_path}")
    
    # 启动浏览器，指定执行路径
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
    
    # 获取项目根目录的绝对路径
    base_dir = os.path.abspath('')
    
    for html_file in html_files:
        # 构建文件路径
        file_path = os.path.join(html_dir, html_file)
        # 构建输出路径
        pdf_filename = os.path.splitext(html_file)[0] + '.pdf'
        pdf_path = os.path.join(output_dir, pdf_filename)
        
        print(f"处理: {html_file}")
        
        # 创建页面
        page = await browser.newPage()
        
        # 设置视口大小
        await page.setViewport({'width': width, 'height': height})
        
        # 获取文件所在目录的绝对路径，用于正确加载资源
        file_dir = os.path.dirname(os.path.abspath(file_path))
        
        # 访问本地文件 (使用绝对路径)
        file_url = f"file://{os.path.abspath(file_path)}"
        
        # 设置页面导航选项，确保资源加载完成
        navigation_options = {
            'waitUntil': ['load', 'networkidle0', 'domcontentloaded'],
            'timeout': 60000  # 增加超时时间为60秒
        }
        
        # 导航到页面
        await page.goto(file_url, navigation_options)
        
        # 额外等待以确保动态内容和图片加载完成
        await asyncio.sleep(2)
        
        # 在页面加载后检查图片是否全部加载完成
        images_loaded = await page.evaluate('''() => {
            const images = Array.from(document.querySelectorAll('img'));
            return images.every(img => img.complete);
        }''')
        
        if not images_loaded:
            print("  ⚠️ 等待图片加载完成...")
            # 如果图片未完全加载，再等待一段时间
            await asyncio.sleep(3)
        
        # 使用CSS选择器找到内容部分
        content_selector = '.slide-container'
        
        try:
            # 等待内容元素加载完成
            await page.waitForSelector(content_selector, {'timeout': 10000})
            
            # 获取内容元素的尺寸和位置
            content_box = await page.evaluate(f'''() => {{
                const element = document.querySelector('{content_selector}');
                if (!element) return null;
                const rect = element.getBoundingClientRect();
                return {{
                    x: rect.x,
                    y: rect.y,
                    width: rect.width,
                    height: rect.height
                }};
            }}''')
            
            if content_box:
                # 导出PDF，剪裁到内容部分
                await page.pdf({
                    'path': pdf_path,
                    'width': f"{content_box['width']}px",
                    'height': f"{content_box['height']}px",
                    'printBackground': True,  # 打印背景
                    'preferCSSPageSize': True,  # 优先使用CSS页面尺寸
                    'margin': {'top': 0, 'right': 0, 'bottom': 0, 'left': 0},
                    'clip': {
                        'x': content_box['x'],
                        'y': content_box['y'],
                        'width': content_box['width'],
                        'height': content_box['height']
                    }
                })
                print(f"✅ 成功导出: {pdf_path}")
            else:
                # 如果找不到内容元素，则导出整个页面
                await page.pdf({
                    'path': pdf_path,
                    'width': f"{width}px",
                    'height': f"{height}px",
                    'printBackground': True,
                    'preferCSSPageSize': True,
                })
                print(f"⚠️ 无法找到内容元素，已导出整个页面: {pdf_path}")
        except Exception as e:
            print(f"❌ 处理 {html_file} 时出错: {e}")
            # 导出整个页面作为备选
            try:
                await page.pdf({
                    'path': pdf_path,
                    'format': 'A4',
                    'printBackground': True,
                    'preferCSSPageSize': True,
                })
                print(f"⚠️ 已导出整个页面: {pdf_path}")
            except Exception as e2:
                print(f"❌ 无法导出PDF: {e2}")
        
        # 关闭页面
        await page.close()
    
    # 关闭浏览器
    await browser.close()
    print("所有PDF导出完成!")
    
    # 合并PDF文件
    merge_pdfs(output_dir, os.path.join(output_dir, merged_output))

def merge_pdfs(pdf_dir, output_path):
    """合并目录中的所有PDF文件为一个文件"""
    try:
        # 获取所有PDF文件并按文件名排序
        pdf_files = sorted(
            [f for f in glob.glob(f"{pdf_dir}/*.pdf") if os.path.basename(f) != os.path.basename(output_path)],
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
        merger.write(output_path)
        merger.close()
        
        print(f"✅ 所有PDF已合并为: {output_path}")
    except Exception as e:
        print(f"❌ 合并PDF时出错: {e}")

# 运行异步函数
if __name__ == "__main__":
    try:
        asyncio.run(export_to_pdf())
    except AttributeError:
        # 对于Python 3.6及更早版本
        asyncio.get_event_loop().run_until_complete(export_to_pdf()) 