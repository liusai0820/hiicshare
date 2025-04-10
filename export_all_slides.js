const puppeteer = require('puppeteer-core');
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

// 创建一个sleep函数
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// 查找Chrome路径
function findChromePath() {
  // macOS上的常见Chrome路径
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

  // 尝试使用which命令查找
  try {
    return execSync('which google-chrome || which chrome || which chromium').toString().trim();
  } catch (e) {
    return null;
  }
}

// 主函数
async function exportAllSlides() {
  console.log('开始导出HTML到PDF...');
  
  // 查找Chrome路径
  const chromePath = findChromePath();
  if (!chromePath) {
    throw new Error('无法找到Chrome浏览器，请确保已安装Google Chrome');
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
  
  // 启动浏览器
  const browser = await puppeteer.launch({
    headless: true,
    executablePath: chromePath,
    defaultViewport: { width, height },
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-web-security',
      '--allow-file-access-from-files',
      `--window-size=${width},${height}`,
    ]
  });
  
  const allPdfFiles = []; // 存储所有PDF文件路径
  
  try {
    for (const htmlFile of htmlFiles) {
      // 构建文件路径
      const filePath = path.join(htmlDir, htmlFile);
      const baseName = path.basename(htmlFile, '.html');
      
      console.log(`处理: ${htmlFile}`);
      
      // 创建页面
      const page = await browser.newPage();
      
      try {
        // 访问本地文件（使用绝对路径）
        const fileUrl = `file://${path.resolve(filePath)}`;
        
        // 导航到页面
        await page.goto(fileUrl, { 
          waitUntil: ['load', 'networkidle0'],
          timeout: 30000 
        });
        
        // 等待内容加载完成
        await sleep(2000);
        
        // 移除所有导航元素
        await page.evaluate(() => {
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
        });
        
        // 检查页面是否包含多页内容
        const hasMultiplePages = await page.evaluate(() => {
          // 检查页码指示器中是否有斜杠，如 "1/3"
          const pageIndicators = document.querySelectorAll('.page-number');
          for (let indicator of pageIndicators) {
            const text = indicator.textContent.trim();
            if (text.includes('/')) {
              return true;
            }
          }
          
          // 检查是否有下一页按钮
          const nextButtons = document.querySelectorAll('button[id$="-next"], .next-btn, .next');
          return nextButtons.length > 0;
        });
        
        if (hasMultiplePages) {
          console.log('  检测到多页内容');
          
          // 获取总页数
          const totalPages = await page.evaluate(() => {
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
          });
          
          console.log(`  估计总页数: ${totalPages}`);
          
          // 为每一页创建PDF
          for (let pageNum = 1; pageNum <= totalPages; pageNum++) {
            // 生成PDF文件名，包含子页码
            const pdfFilename = `${baseName}-${pageNum}.pdf`;
            const pdfPath = path.join(outputDir, pdfFilename);
            
            // 导出当前页面为PDF
            await page.pdf({
              path: pdfPath,
              width: `${width}px`,
              height: `${height}px`,
              printBackground: true,
              margin: { top: 0, right: 0, bottom: 0, left: 0 }
            });
            
            console.log(`  ✅ 导出第 ${pageNum} 页: ${pdfPath}`);
            allPdfFiles.push(pdfPath);
            
            // 如果不是最后一页，点击下一页按钮
            if (pageNum < totalPages) {
              await page.evaluate(() => {
                // 尝试点击下一页按钮
                const nextButtons = document.querySelectorAll('button[id$="-next"], .next-btn, .next');
                if (nextButtons.length > 0) {
                  nextButtons[0].click();
                }
              });
              
              // 等待页面切换
              await sleep(1000);
            }
          }
        } else {
          // 单页内容，直接导出
          const pdfFilename = `${baseName}.pdf`;
          const pdfPath = path.join(outputDir, pdfFilename);
          
          // 导出PDF
          await page.pdf({
            path: pdfPath,
            width: `${width}px`,
            height: `${height}px`,
            printBackground: true,
            margin: { top: 0, right: 0, bottom: 0, left: 0 }
          });
          
          console.log(`  ✅ 导出单页: ${pdfPath}`);
          allPdfFiles.push(pdfPath);
        }
      } catch (error) {
        console.error(`❌ 处理 ${htmlFile} 时出错:`, error);
      } finally {
        await page.close();
      }
    }
  } finally {
    // 关闭浏览器
    await browser.close();
  }
  
  console.log('所有PDF导出完成!');
  
  // 合并所有PDF文件
  if (allPdfFiles.length > 0) {
    await mergePdfs(allPdfFiles, path.join(outputDir, mergedOutput));
  }
}

// 合并PDF文件
async function mergePdfs(pdfFiles, outputPath) {
  if (pdfFiles.length === 0) return;
  
  console.log(`尝试合并 ${pdfFiles.length} 个PDF文件...`);
  
  // 尝试使用系统工具合并PDF
  try {
    // 方法1: 使用pdftk
    const cmd = `pdftk ${pdfFiles.join(' ')} cat output "${outputPath}"`;
    execSync(cmd);
    console.log(`✅ 所有PDF已使用pdftk合并为: ${outputPath}`);
    return;
  } catch (error) {
    console.log('使用pdftk合并失败，尝试其他方法...');
  }
  
  try {
    // 方法2: 使用ghostscript
    const cmd = `gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile="${outputPath}" ${pdfFiles.join(' ')}`;
    execSync(cmd);
    console.log(`✅ 所有PDF已使用ghostscript合并为: ${outputPath}`);
    return;
  } catch (error) {
    console.log('使用ghostscript合并失败...');
  }
  
  // 方法3: 在macOS上尝试使用自带工具
  if (process.platform === 'darwin') {
    try {
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
exportAllSlides()
  .then(() => {
    console.log('导出过程成功完成');
    process.exit(0);
  })
  .catch(error => {
    console.error('导出过程中发生错误:', error);
    process.exit(1);
  }); 