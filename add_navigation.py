import os
import glob
import re

# --- 配置 ---
html_dir = 'html-ppt'  # HTML文件所在的目录

# HTML代码：添加全屏模式下的导航按钮和控制面板
navigation_html = '''
<div id="fs-nav" style="position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background-color: rgba(0,0,0,0.5); color: white; padding: 8px 15px; border-radius: 8px; display: none; z-index: 9999; align-items: center; gap: 10px;">
  <button id="fs-prev-btn" style="background-color: #4CAF50; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer;">&lt; 上一页</button>
  <span id="fs-page-info" style="font-size: 14px; color: white;">页面</span>
  <button id="fs-next-btn" style="background-color: #4CAF50; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer;">下一页 &gt;</button>
</div>
'''

# JavaScript代码：处理全屏导航逻辑
navigation_js = '''
<script>
  // 等待页面加载完成
  document.addEventListener('DOMContentLoaded', () => {
    // 获取全屏导航元素
    const fsNav = document.getElementById('fs-nav');
    const fsPrevBtn = document.getElementById('fs-prev-btn');
    const fsNextBtn = document.getElementById('fs-next-btn');
    const fsPageInfo = document.getElementById('fs-page-info');
    
    // 全屏按钮
    const fsBtn = document.getElementById('fs-btn');
    
    // 当进入或退出全屏时，显示或隐藏导航
    document.addEventListener('fullscreenchange', () => {
      if (document.fullscreenElement) {
        fsNav.style.display = 'flex';  // 全屏时显示
        // 尝试从父窗口获取当前页面信息
        try {
          const url = window.location.href;
          const fileName = url.substring(url.lastIndexOf('/') + 1);
          // 发送消息给父窗口获取当前页面信息
          window.parent.postMessage({type: 'getPageInfo', fileName: fileName}, '*');
        } catch (e) {
          console.error('无法获取页面信息:', e);
        }
      } else {
        fsNav.style.display = 'none';  // 非全屏时隐藏
      }
    });
    
    // 处理上一页按钮点击
    fsPrevBtn.addEventListener('click', () => {
      // 发送消息给父窗口，请求切换到上一页
      window.parent.postMessage({type: 'prevPage'}, '*');
    });
    
    // 处理下一页按钮点击
    fsNextBtn.addEventListener('click', () => {
      // 发送消息给父窗口，请求切换到下一页
      window.parent.postMessage({type: 'nextPage'}, '*');
    });
    
    // 接收来自父窗口的消息
    window.addEventListener('message', (event) => {
      // 安全检查可以根据实际情况添加
      const data = event.data;
      
      // 如果收到页面信息更新
      if (data.type === 'pageInfoUpdate') {
        fsPageInfo.textContent = data.info;
        
        // 更新按钮状态
        fsPrevBtn.disabled = data.isFirst;
        fsPrevBtn.style.opacity = data.isFirst ? '0.5' : '1';
        fsNextBtn.disabled = data.isLast;
        fsNextBtn.style.opacity = data.isLast ? '0.5' : '1';
      }
    });
  });
</script>
'''

# --- 主逻辑 ---
def add_navigation():
    html_files = glob.glob(os.path.join(html_dir, '*.html'))
    if not html_files:
        print(f"错误：在 '{html_dir}' 目录下没有找到任何 .html 文件。")
        return

    print(f"找到 {len(html_files)} 个 HTML 文件。开始添加导航...")

    for filepath in html_files:
        print(f"  正在处理: {filepath}")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查是否已经添加了fs-nav
            if 'id="fs-nav"' in content:
                print(f"    - 导航元素已存在，跳过")
                continue

            # 查找 </body> 标签
            body_end_tag = '</body>'
            body_end_index = content.rfind(body_end_tag)

            if body_end_index != -1:
                # 在 </body> 前插入导航 HTML 和 JS
                insertion_point = body_end_index
                new_content = content[:insertion_point] + navigation_html.strip() + '\n' + navigation_js.strip() + '\n' + content[insertion_point:]

                # 写回文件
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"    - 添加了全屏导航")
            else:
                print(f"    ! 警告: 在 {filepath} 中未找到 </body> 标签，跳过添加")

        except Exception as e:
            print(f"    ! 错误: 处理 {filepath} 时发生错误: {e}")

    print("导航添加完成。")

if __name__ == "__main__":
    add_navigation() 