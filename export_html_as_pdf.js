const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 配置
const htmlDir = 'html-ppt'; // HTML文件所在的目录
const outputDir = 'pdf-output'; // 输出PDF的目录
const mergedOutput = 'presentation.pdf'; // 合并后的PDF文件名
const width = 1280; // 导出宽度
const height = 720; // 导出高度

// 确保输出目录存在
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

// 主函数
function exportToPdf() {
  console.log('开始导出HTML到PDF...');
  
  // 查找Chrome浏览器路径
  const chromePath = findChrome();
  
  if (!chromePath) {
    console.error('❌ 无法找到Chrome浏览器。请确保已安装Google Chrome。');
    process.exit(1);
  }
  
  console.log(`✅ 找到Chrome浏览器: ${chromePath}`);
  
  // 获取所有HTML文件并按文件名排序
  let htmlFiles = fs.readdirSync(htmlDir)
    .filter(file => file.endsWith('.html'))
    .sort((a, b) => {
      const numA = parseInt(a.split('-')[0]) || 999;
      const numB = parseInt(b.split('-')[0]) || 999;
      return numA - numB;
    });
  
  console.log(`找到 ${htmlFiles.length} 个HTML文件`);
  
  // 导出的PDF文件路径数组
  const pdfFiles = [];

  for (const htmlFile of htmlFiles) {
    // 构建文件路径
    const filePath = path.join(htmlDir, htmlFile);
    // 构建输出路径
    const pdfFilename = htmlFile.replace('.html', '.pdf');
    const pdfPath = path.join(outputDir, pdfFilename);
    
    console.log(`处理: ${htmlFile}`);
    
    try {
      // 使用Chrome的headless模式直接打印PDF
      const fileUrl = `file://${path.resolve(filePath)}`;
      
      // 使用新的 headless=new 模式
      const chromeArgs = [
        '--headless=new',  // 新的headless模式
        '--disable-gpu',
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--allow-file-access-from-files',
        `--window-size=${width},${height}`,
        '--run-all-compositor-stages-before-draw',
        '--no-pdf-header-footer',
        `--print-to-pdf=${path.resolve(pdfPath)}`,
        '--no-default-browser-check', 
        fileUrl
      ];
      
      // 执行Chrome命令
      execSync(`"${chromePath}" ${chromeArgs.join(' ')}`, { 
        stdio: 'pipe',
        timeout: 60000 // 60秒超时
      });
      
      console.log(`✅ 成功导出: ${pdfPath}`);
      pdfFiles.push(pdfPath);
    } catch (error) {
      console.error(`❌ 处理 ${htmlFile} 时出错:`, error.message);
      
      // 尝试备选方法，使用截图
      try {
        console.log(`  尝试备选方法: 使用截图...`);
        
        // 使用Chrome截图并转换为PDF
        const screenshotPath = path.join(outputDir, `${path.basename(pdfPath, '.pdf')}.png`);
        
        const screenshotArgs = [
          '--headless=new',
          '--disable-gpu',
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--allow-file-access-from-files',
          `--window-size=${width},${height}`,
          '--hide-scrollbars',
          `--screenshot=${screenshotPath}`,
          '--default-background-color=0',
          fileUrl
        ];
        
        execSync(`"${chromePath}" ${screenshotArgs.join(' ')}`, {
          stdio: 'pipe',
          timeout: 60000
        });
        
        console.log(`  ✅ 成功截图: ${screenshotPath}`);
        
        // 转换PNG截图为PDF (使用系统命令如果可用)
        try {
          // 尝试使用Mac的sips和convert命令
          if (process.platform === 'darwin') {
            execSync(`/usr/bin/sips -s format pdf "${screenshotPath}" --out "${pdfPath}"`, {
              stdio: 'pipe'
            });
            
            // 删除临时PNG文件
            fs.unlinkSync(screenshotPath);
            
            console.log(`  ✅ 成功转换为PDF: ${pdfPath}`);
            pdfFiles.push(pdfPath);
          } else {
            console.log(`  ⚠️ 无法转换截图为PDF，跳过此文件`);
          }
        } catch (e) {
          console.error(`  ❌ 转换截图为PDF失败:`, e.message);
        }
      } catch (screenshotError) {
        console.error(`  ❌ 截图也失败了:`, screenshotError.message);
      }
    }
  }
  
  console.log('所有PDF导出完成!');
  
  // 合并PDF文件（如果有系统工具可用）
  if (pdfFiles.length > 0) {
    tryMergePdfs(pdfFiles, path.join(outputDir, mergedOutput));
  }
}

// 查找Chrome浏览器路径
function findChrome() {
  // MacOS上的常见Chrome路径
  const possiblePaths = [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary',
    '/Applications/Chromium.app/Contents/MacOS/Chromium'
  ];
  
  for (const path of possiblePaths) {
    if (fs.existsSync(path)) {
      return path;
    }
  }
  
  // 尝试用which命令查找
  try {
    return execSync('which google-chrome || which chrome || which chromium').toString().trim();
  } catch (error) {
    return null;
  }
}

// 尝试合并PDF文件
function tryMergePdfs(pdfFiles, outputPath) {
  if (pdfFiles.length === 0) return;
  
  console.log(`尝试合并 ${pdfFiles.length} 个PDF文件...`);
  
  // 尝试使用系统工具合并PDF
  
  // 方法1: 使用pdftk
  try {
    const cmd = `pdftk ${pdfFiles.join(' ')} cat output "${outputPath}"`;
    execSync(cmd);
    console.log(`✅ 所有PDF已使用pdftk合并为: ${outputPath}`);
    return;
  } catch (error) {
    console.log('使用pdftk合并失败，尝试其他方法...');
  }
  
  // 方法2: 使用ghostscript
  try {
    const cmd = `gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile="${outputPath}" ${pdfFiles.join(' ')}`;
    execSync(cmd);
    console.log(`✅ 所有PDF已使用ghostscript合并为: ${outputPath}`);
    return;
  } catch (error) {
    console.log('使用ghostscript合并失败...');
  }
  
  // 方法3: 在macOS上尝试使用/System/Library/Automator/Combine PDF Pages.action
  if (process.platform === 'darwin') {
    try {
      // 使用macOS自带的工具合并PDF
      execSync(`/System/Library/Automator/Combine\\ PDF\\ Pages.action/Contents/Resources/join.py -o "${outputPath}" ${pdfFiles.join(' ')}`, {
        stdio: 'pipe'
      });
      console.log(`✅ 所有PDF已使用macOS自带工具合并为: ${outputPath}`);
      return;
    } catch (error) {
      console.log('使用macOS自带工具合并失败...');
    }
  }
  
  console.log(`⚠️ 无法自动合并PDF文件。所有单独的PDF文件仍保存在 ${outputDir} 目录中。`);
}

// 执行主函数
try {
  exportToPdf();
} catch (error) {
  console.error('导出过程中发生错误:', error);
  process.exit(1);
} 