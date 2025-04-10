const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 配置
const htmlDir = 'html-ppt'; // HTML文件所在的目录
const outputDir = 'pdf-output'; // 输出PDF的目录
const targetFile = process.argv[2] || '6-aihiic.html'; // 从命令行参数获取要导出的目标文件
const width = 1280; // 导出宽度
const height = 720; // 导出高度

// 确保输出目录存在
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

// 创建一个sleep函数代替waitForTimeout
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
async function exportToPdf() {
  console.log('开始导出单个HTML到PDF...');
  
  // 查找Chrome路径
  const chromePath = findChromePath();
  if (!chromePath) {
    throw new Error('无法找到Chrome浏览器，请确保已安装Google Chrome');
  }
  console.log(`✅ 找到Chrome浏览器: ${chromePath}`);
  
  // 构建文件路径
  const filePath = path.join(htmlDir, targetFile);
  // 构建输出路径
  const pdfFilename = targetFile.replace('.html', '.pdf');
  const pdfPath = path.join(outputDir, pdfFilename);
  
  console.log(`处理: ${targetFile}`);
  
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
  
  try {
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
      
      // 等待内容加载完成（使用自定义sleep函数替代waitForTimeout）
      await sleep(2000);
      
      // 设置页面日志监听
      page.on('console', msg => {
        console.log(`页面日志: ${msg.text()}`);
      });
      
      // 修改页面样式，确保打印时包含背景颜色和图片
      await page.evaluate(() => {
        const style = document.createElement('style');
        style.innerHTML = `
          @media print {
            * {
              -webkit-print-color-adjust: exact !important;
              print-color-adjust: exact !important;
            }
            body {
              margin: 0;
              padding: 0;
            }
            img {
              display: block !important;
              break-inside: avoid !important;
            }
            .slide-container {
              page-break-after: always;
            }
          }
        `;
        document.head.appendChild(style);
      });
      
      // 等待所有图片加载完成
      const imagesLoaded = await page.evaluate(async () => {
        const imgElements = Array.from(document.querySelectorAll('img'));
        console.log(`找到 ${imgElements.length} 个图片元素`);
        
        if (imgElements.length === 0) return true;
        
        // 修复图片路径
        imgElements.forEach(img => {
          // 如果是相对路径，尝试修复
          if (img.src.startsWith('..')) {
            const newSrc = img.src.replace(/^\.\./g, '');
            console.log(`修复图片路径: ${img.src} -> ${newSrc}`);
            img.src = newSrc;
          }
          // 显示当前图片路径
          console.log(`图片路径: ${img.src}, 是否已加载: ${img.complete}`);
        });
        
        // 使用Promise.all等待所有图片加载
        await Promise.all(imgElements.map(img => {
          if (img.complete) return Promise.resolve();
          
          return new Promise((resolve) => {
            img.addEventListener('load', () => {
              console.log(`图片已加载: ${img.src}`);
              resolve();
            });
            img.addEventListener('error', () => {
              console.error(`图片加载失败: ${img.src}`);
              resolve(); // 即使错误也继续
            });
            
            // 设置超时，防止无限等待
            setTimeout(resolve, 5000);
          });
        }));
        
        return true;
      });
      
      console.log(`图片加载状态: ${imagesLoaded ? '所有图片已加载' : '部分图片未加载'}`);
      
      // 再次等待，确保所有内容都已完全加载
      await sleep(1000);
      
      // 导出PDF - 尝试直接导出整个页面
      await page.pdf({
        path: pdfPath,
        width: `${width}px`,
        height: `${height}px`,
        printBackground: true,
        margin: { top: 0, right: 0, bottom: 0, left: 0 },
        preferCSSPageSize: true,
      });
      
      console.log(`✅ 成功导出: ${pdfPath}`);
    } catch (error) {
      console.error(`❌ 处理 ${targetFile} 时出错:`, error);
    } finally {
      await page.close();
    }
  } finally {
    // 关闭浏览器
    await browser.close();
  }
  
  console.log('PDF导出完成!');
}

// 执行主函数
exportToPdf()
  .then(() => {
    console.log('导出过程成功完成');
    process.exit(0);
  })
  .catch(error => {
    console.error('导出过程中发生错误:', error);
    process.exit(1);
  }); 