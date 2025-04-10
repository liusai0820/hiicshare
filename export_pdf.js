const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const { PDFDocument } = require('pdf-lib');

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
async function exportToPdf() {
  console.log('开始导出HTML到PDF...');
  
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
    headless: 'new', // 使用新的无头模式
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--allow-file-access-from-files', // 允许从文件加载资源
    ]
  });
  
  // 获取项目根目录的绝对路径
  const baseDir = path.resolve();
  
  // 导出的PDF文件路径数组
  const pdfFiles = [];

  for (const htmlFile of htmlFiles) {
    // 构建文件路径
    const filePath = path.join(htmlDir, htmlFile);
    // 构建输出路径
    const pdfFilename = htmlFile.replace('.html', '.pdf');
    const pdfPath = path.join(outputDir, pdfFilename);
    
    console.log(`处理: ${htmlFile}`);
    
    // 创建页面
    const page = await browser.newPage();
    
    // 设置视口大小
    await page.setViewport({ width, height });
    
    try {
      // 访问本地文件（使用绝对路径）
      const fileUrl = `file://${path.resolve(filePath)}`;
      
      // 导航到页面并等待加载完成
      await page.goto(fileUrl, {
        waitUntil: ['load', 'networkidle0', 'domcontentloaded'],
        timeout: 60000 // 超时时间60秒
      });
      
      // 等待以确保动态内容和图片加载完成
      await page.waitForTimeout(2000);
      
      // 检查图片是否加载完成
      const imagesLoaded = await page.evaluate(() => {
        const images = Array.from(document.querySelectorAll('img'));
        return images.every(img => img.complete);
      });
      
      if (!imagesLoaded) {
        console.log('  ⚠️ 等待图片加载完成...');
        await page.waitForTimeout(3000);
      }
      
      // 使用CSS选择器找到内容部分
      const contentSelector = '.slide-container';
      
      // 等待内容元素加载完成
      await page.waitForSelector(contentSelector, { timeout: 10000 });
      
      // 获取内容元素的尺寸和位置
      const contentBox = await page.evaluate((selector) => {
        const element = document.querySelector(selector);
        if (!element) return null;
        
        const rect = element.getBoundingClientRect();
        return {
          x: rect.x,
          y: rect.y,
          width: rect.width,
          height: rect.height
        };
      }, contentSelector);
      
      if (contentBox) {
        // 导出PDF，剪裁到内容部分
        await page.pdf({
          path: pdfPath,
          width: `${contentBox.width}px`,
          height: `${contentBox.height}px`,
          printBackground: true,
          preferCSSPageSize: true,
          margin: { top: 0, right: 0, bottom: 0, left: 0 },
          clip: {
            x: contentBox.x,
            y: contentBox.y,
            width: contentBox.width,
            height: contentBox.height
          }
        });
        console.log(`✅ 成功导出: ${pdfPath}`);
        pdfFiles.push(pdfPath);
      } else {
        // 如果找不到内容元素，则导出整个页面
        await page.pdf({
          path: pdfPath,
          width: `${width}px`,
          height: `${height}px`,
          printBackground: true,
          preferCSSPageSize: true
        });
        console.log(`⚠️ 无法找到内容元素，已导出整个页面: ${pdfPath}`);
        pdfFiles.push(pdfPath);
      }
    } catch (error) {
      console.error(`❌ 处理 ${htmlFile} 时出错:`, error);
      
      try {
        // 导出整个页面作为备选
        await page.pdf({
          path: pdfPath,
          format: 'A4',
          printBackground: true
        });
        console.log(`⚠️ 已导出整个页面（备选方案）: ${pdfPath}`);
        pdfFiles.push(pdfPath);
      } catch (e) {
        console.error(`❌ 无法导出PDF:`, e);
      }
    }
    
    // 关闭页面
    await page.close();
  }
  
  // 关闭浏览器
  await browser.close();
  console.log('所有PDF导出完成!');
  
  // 合并PDF文件
  if (pdfFiles.length > 0) {
    const pdfToolsAvailable = await isPdfToolsAvailable();
    if (pdfToolsAvailable) {
      await mergePdfs(pdfFiles, path.join(outputDir, mergedOutput));
    } else {
      console.log('⚠️ 没有找到PDF合并工具，跳过合并步骤。您可以手动合并PDF文件或安装必要的工具。');
    }
  }
}

// 检查PDF合并工具是否可用
async function isPdfToolsAvailable() {
  try {
    require('pdf-lib');
    return true;
  } catch (error) {
    console.log('⚠️ pdf-lib 未安装，尝试使用系统工具');
    
    // 尝试检查是否有系统级的PDF工具
    try {
      const { execSync } = require('child_process');
      // 尝试使用pdftk或ghostscript
      execSync('which pdftk || which gs', { stdio: 'ignore' });
      return true;
    } catch (error) {
      return false;
    }
  }
}

// 合并PDF文件
async function mergePdfs(pdfFiles, outputPath) {
  console.log(`开始合并 ${pdfFiles.length} 个PDF文件...`);
  
  try {
    // 尝试使用pdf-lib
    try {
      const PDFDocument = require('pdf-lib').PDFDocument;
      const fs = require('fs').promises;
      
      const mergedPdf = await PDFDocument.create();
      
      for (const pdfPath of pdfFiles) {
        try {
          const pdfBytes = await fs.readFile(pdfPath);
          const pdf = await PDFDocument.load(pdfBytes);
          const copiedPages = await mergedPdf.copyPages(pdf, pdf.getPageIndices());
          copiedPages.forEach(page => mergedPdf.addPage(page));
          console.log(`  已添加: ${path.basename(pdfPath)}`);
        } catch (e) {
          console.error(`  ❌ 无法添加 ${path.basename(pdfPath)}:`, e);
        }
      }
      
      const mergedPdfBytes = await mergedPdf.save();
      await fs.writeFile(outputPath, mergedPdfBytes);
      
      console.log(`✅ 所有PDF已合并为: ${outputPath}`);
      return;
    } catch (error) {
      console.log('使用pdf-lib合并失败，尝试使用系统工具:', error);
    }
    
    // 备选：使用系统工具
    const { execSync } = require('child_process');
    
    // 尝试使用pdftk
    try {
      const cmd = `pdftk ${pdfFiles.join(' ')} cat output "${outputPath}"`;
      execSync(cmd);
      console.log(`✅ 所有PDF已使用pdftk合并为: ${outputPath}`);
      return;
    } catch (error) {
      console.log('使用pdftk合并失败，尝试使用ghostscript:', error);
    }
    
    // 尝试使用ghostscript
    try {
      const cmd = `gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile="${outputPath}" ${pdfFiles.join(' ')}`;
      execSync(cmd);
      console.log(`✅ 所有PDF已使用ghostscript合并为: ${outputPath}`);
      return;
    } catch (error) {
      console.error('使用ghostscript合并失败:', error);
    }
    
    throw new Error('所有PDF合并方法都失败了');
  } catch (error) {
    console.error(`❌ 合并PDF时出错:`, error);
  }
}

// 执行主函数
exportToPdf().catch(error => {
  console.error('导出过程中发生错误:', error);
  process.exit(1);
}); 