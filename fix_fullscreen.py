import os
import glob
import re

# --- 配置 ---
html_dir = 'html-ppt'  # HTML文件所在的目录
button_html = '''
<button id="fs-btn" style="position: fixed; top: 10px; right: 10px; z-index: 9999; padding: 5px 10px; font-size: 12px; cursor: pointer; background-color: rgba(0,0,0,0.5); color: white; border: none; border-radius: 4px;">全屏</button>
'''
button_js = '''
<script>
  document.addEventListener('DOMContentLoaded', () => {
    const fsBtn = document.getElementById('fs-btn');
    if (fsBtn) {
      fsBtn.addEventListener('click', () => {
        if (!document.fullscreenElement) {
          // 找到幻灯片容器元素进行全屏，而不是整个文档
          const slideContainer = document.querySelector('.slide-container');
          if (slideContainer) {
            slideContainer.requestFullscreen().catch(err => {
              console.error(`无法进入全屏模式: ${err.message} (${err.name})`);
            });
          } else {
            // 如果找不到 .slide-container，退而求其次用文档元素
            document.documentElement.requestFullscreen().catch(err => {
              console.error(`无法进入全屏模式: ${err.message} (${err.name})`);
            });
          }
        } else {
          // 退出全屏
          if (document.exitFullscreen) {
            document.exitFullscreen();
          }
        }
      });

      // 监听全屏状态变化，更新按钮文本
      document.addEventListener('fullscreenchange', () => {
        if (document.fullscreenElement) {
          fsBtn.textContent = '退出';
        } else {
          fsBtn.textContent = '全屏';
        }
      });
    }
  });
</script>
'''

# 匹配旧的全屏按钮和脚本
old_fs_button_pattern = re.compile(r'<button id="fs-btn".*?</button>', re.DOTALL)
old_fs_script_pattern = re.compile(r'<script>\s*document\.addEventListener\(\'DOMContentLoaded\',\s*\(\)\s*=>\s*\{.*?fsBtn.*?\}\);\s*</script>', re.DOTALL)

# 匹配旧的 postMessage 监听器代码
old_postmessage_pattern = re.compile(r'<script>\s*window\.addEventListener\(\'message\',\s*\(event\)\s*=>\s*\{.*?\s*\}\);\s*</script>', re.DOTALL)

# --- 主逻辑 ---
def fix_fullscreen():
    html_files = glob.glob(os.path.join(html_dir, '*.html'))
    if not html_files:
        print(f"错误：在 '{html_dir}' 目录下没有找到任何 .html 文件。")
        return

    print(f"找到 {len(html_files)} 个 HTML 文件。开始修复...")

    for filepath in html_files:
        print(f"  正在处理: {filepath}")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # 1. 移除旧的全屏按钮和脚本 (如果存在)
            content, btn_replacements = old_fs_button_pattern.subn('', content)
            content, script_replacements = old_fs_script_pattern.subn('', content)
            if btn_replacements > 0 or script_replacements > 0:
                print(f"    - 移除了旧的全屏按钮和脚本")

            # 2. 移除旧的 postMessage 监听器 (如果存在)
            content, pm_replacements = old_postmessage_pattern.subn('', content)
            if pm_replacements > 0:
                print(f"    - 移除了旧的 postMessage 监听脚本")

            # 3. 查找 </body> 标签并插入新内容
            body_end_tag = '</body>'
            body_end_index = content.rfind(body_end_tag)

            if body_end_index != -1:
                # 在 </body> 前插入按钮 HTML 和按钮 JS
                insertion_point = body_end_index
                new_content = content[:insertion_point] + button_html.strip() + '\n' + button_js.strip() + '\n' + content[insertion_point:]

                # 4. 写回文件
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"    - 添加了改进的全屏按钮和脚本")
            else:
                print(f"    ! 警告: 在 {filepath} 中未找到 </body> 标签，跳过添加")

        except Exception as e:
            print(f"    ! 错误: 处理 {filepath} 时发生错误: {e}")

    print("修复完成。")

if __name__ == "__main__":
    fix_fullscreen() 