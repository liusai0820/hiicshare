document.addEventListener('DOMContentLoaded', () => {
    const pptFrame = document.getElementById('ppt-frame');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const pageInfo = document.getElementById('page-info');
    // 移除全屏按钮相关代码
    // const fullscreenBtn = document.getElementById('fullscreen-btn');

    // 注意：请确保这些文件名与 html-ppt 文件夹中的实际文件名和顺序一致
    const pages = [
        'html-ppt/1-start.html',
        'html-ppt/2-lobe1.html',
        'html-ppt/2-lobe2.html',
        'html-ppt/2-lobe3.html',
        'html-ppt/3-chain1.html',
        'html-ppt/3-chain2.html',
        'html-ppt/3-chain3.html',
        'html-ppt/3-chain4.html',
        'html-ppt/4-aislide1.html',
        'html-ppt/4-aislide2.html',
        'html-ppt/4-aislide3.html',
        'html-ppt/5-xie1.html',
        'html-ppt/5-xie2.html',
        'html-ppt/5-xie3.html',
        'html-ppt/6-aihiic.html',
        'html-ppt/7-model.html',
        'html-ppt/8-end.html',
    ];

    // 直接使用所有页面，不再过滤
    const filteredPages = pages;
    
    let currentPageIndex = 0;
    const totalPages = filteredPages.length;

    function loadPage(index) {
        if (index >= 0 && index < totalPages) {
            pptFrame.src = filteredPages[index];
            currentPageIndex = index;
            updateControls();
        }
    }

    function updateControls() {
        pageInfo.textContent = `第 ${currentPageIndex + 1} / ${totalPages} 页`;
        prevBtn.disabled = currentPageIndex === 0;
        nextBtn.disabled = currentPageIndex === totalPages - 1;
    }

    prevBtn.addEventListener('click', () => {
        loadPage(currentPageIndex - 1);
    });

    nextBtn.addEventListener('click', () => {
        loadPage(currentPageIndex + 1);
    });

    // 添加：处理来自 iframe 的消息
    window.addEventListener('message', (event) => {
        // 尝试解析消息数据
        try {
            const data = event.data;
            
            // 处理各种消息类型
            if (typeof data === 'object') {
                // 处理页面信息请求
                if (data.type === 'getPageInfo') {
                    // 找到当前文件名对应的索引
                    const fileName = data.fileName;
                    let foundIndex = -1;
                    
                    // 在 filteredPages 数组中查找当前文件
                    for (let i = 0; i < filteredPages.length; i++) {
                        if (filteredPages[i].endsWith(fileName)) {
                            foundIndex = i;
                            break;
                        }
                    }
                    
                    if (foundIndex !== -1) {
                        // 发送页面信息回 iframe
                        const iframe = document.getElementById('ppt-frame');
                        iframe.contentWindow.postMessage({
                            type: 'pageInfoUpdate',
                            info: `第 ${foundIndex + 1} / ${totalPages} 页`,
                            isFirst: foundIndex === 0,
                            isLast: foundIndex === totalPages - 1
                        }, '*');
                    }
                }
                // 处理上一页请求
                else if (data.type === 'prevPage') {
                    if (currentPageIndex > 0) {
                        loadPage(currentPageIndex - 1);
                    }
                }
                // 处理下一页请求
                else if (data.type === 'nextPage') {
                    if (currentPageIndex < totalPages - 1) {
                        loadPage(currentPageIndex + 1);
                    }
                }
            }
        } catch (e) {
            console.error('处理 iframe 消息时出错:', e);
        }
    });

    // 移除全屏相关代码
    // fullscreenBtn.addEventListener('click', () => {
    //    toggleFullScreen();
    // });

    // function toggleFullScreen() {
    //    if (!document.fullscreenElement) {
    //        // Send a message to the iframe to request fullscreen internally
    //        if (pptFrame.contentWindow) {
    //            // Send a simple message, or an object like { command: 'fullscreen' }
    //            pptFrame.contentWindow.postMessage('requestFullscreen', '*');
    //            // Note: We can't directly confirm if the iframe succeeded.
    //            // The button text will update based on the document's fullscreen state,
    //            // which might change if the iframe successfully goes fullscreen.
    //        } else {
    //            alert('无法与 iframe 通信。');
    //        }
    //    } else {
    //        // Exit fullscreen - this is always done by the top document
    //        if (document.exitFullscreen) {
    //            document.exitFullscreen();
    //        }
    //    }
    //}

    // 移除全屏状态变化监听
    // document.addEventListener('fullscreenchange', () => {
    //    if (document.fullscreenElement) {
    //        fullscreenBtn.textContent = '退出全屏';
    //    } else {
    //        fullscreenBtn.textContent = '全屏';
    //    }
    // });

    // Initial load
    loadPage(0);
}); 