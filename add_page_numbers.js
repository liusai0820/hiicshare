const fs = require('fs');
const path = require('path');

// HTML文件所在的目录
const htmlDir = 'html-ppt';

// 从文件名中提取数字前缀
function extractNumberPrefix(filename) {
  const match = path.basename(filename).match(/^(\d+)/);
  if (match) {
    return parseInt(match[1], 10);
  }
  return 999; // 如果没有数字前缀，则排在后面
}

// 为所有HTML幻灯片添加页码
function addPageNumbers() {
  try {
    // 获取所有HTML文件
    const htmlFiles = fs.readdirSync(htmlDir)
      .filter(file => file.endsWith('.html'))
      .map(file => path.join(htmlDir, file));
    
    // 按数字前缀排序
    htmlFiles.sort((a, b) => extractNumberPrefix(a) - extractNumberPrefix(b));
    
    const totalFiles = htmlFiles.length;
    console.log(`找到 ${totalFiles} 个HTML文件，开始添加页码...`);
    
    // 为每个文件添加页码
    htmlFiles.forEach((filePath, index) => {
      try {
        // 读取文件内容
        let html = fs.readFileSync(filePath, 'utf-8');
        
        // 查找footer元素
        const footerRegex = /<div class="footer"[^>]*>([\s\S]*?)<\/div>\s*<\/div>\s*<\/body>/i;
        const footerMatch = html.match(footerRegex);
        
        if (!footerMatch) {
          console.log(`警告: 在 ${path.basename(filePath)} 中没有找到footer元素，尝试添加footer`);
          
          // 尝试在body结束前添加footer
          const pageNumber = index + 1;
          const newFooter = 
            `<div class="footer">
              <div>AI赋能工作效率提升实践分享</div>
              <div class="page-number">${pageNumber}/${totalFiles}</div>
            </div>
          </div>
          </body>`;
          
          html = html.replace(/<\/div>\s*<\/body>/i, newFooter);
        } else {
          // 替换现有footer的内容
          const pageNumber = index + 1;
          const newFooterContent = 
            `<div class="footer">
              <div>AI赋能工作效率提升实践分享</div>
              <div class="page-number">${pageNumber}/${totalFiles}</div>
            </div>`;
          
          html = html.replace(footerRegex, newFooterContent + '</div></body>');
        }
        
        // 保存修改后的文件
        fs.writeFileSync(filePath, html, 'utf-8');
        
        console.log(`✅ 已为 ${path.basename(filePath)} 添加页码 ${index + 1}/${totalFiles}`);
      } catch (e) {
        console.error(`❌ 处理 ${path.basename(filePath)} 时出错: ${e.message}`);
      }
    });
    
    console.log(`✅ 已完成所有${totalFiles}个文件的页码添加`);
  } catch (e) {
    console.error(`❌ 执行过程中出错: ${e.message}`);
  }
}

// 执行添加页码的函数
addPageNumbers(); 