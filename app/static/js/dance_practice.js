// 舞蹈练习页面的JavaScript功能

document.addEventListener('DOMContentLoaded', function() {
  // 获取DOM元素
  const startCameraBtn = document.getElementById('startCameraBtn');
  const startPracticeBtn = document.getElementById('startPracticeBtn');
  const endPracticeBtn = document.getElementById('endPracticeBtn');
  const cameraVideo = document.getElementById('cameraVideo');
  const poseCanvas = document.getElementById('poseCanvas');
  const cameraPlaceholder = document.getElementById('cameraPlaceholder');
  const cameraStatus = document.getElementById('cameraStatus');
  const aiStatus = document.getElementById('aiStatus');
  const practiceTimer = document.getElementById('practiceTimer');
  const practiceProgress = document.getElementById('practiceProgress');
  const currentTime = document.getElementById('currentTime');
  const feedbackList = document.getElementById('feedbackList');
  const searchVideos = document.getElementById('searchVideos');
  const searchQuery = document.getElementById('searchQuery');
  const searchResults = document.getElementById('searchResults');
  
  // 画布上下文
  const ctx = poseCanvas.getContext('2d');
  
  // 状态变量
  let isCameraActive = false;
  let isPracticing = false;
  let practiceTimeSeconds = 0;
  let practiceTimerInterval = null;
  let animationFrameId = null;
  let mediaStream = null;
  
  // 反馈消息池
  const feedbackMessages = [
    '手臂抬高一点',
    '膝盖再弯曲一些',
    '注意保持平衡',
    '动作再流畅一点',
    '很好，继续保持',
    '脚步跟上节奏',
    '上身保持直立',
    '手腕动作很标准',
    '转身再慢一点',
    '表情更自然一些'
  ];
  
  // 开始摄像头函数
  async function startCamera() {
    try {
      // 检查浏览器是否支持媒体设备
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('您的浏览器不支持摄像头功能，请使用现代浏览器。');
      }
      
      // 请求摄像头权限
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'user', // 使用前置摄像头
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      });
      
      mediaStream = stream;
      
      // 设置视频流
      cameraVideo.srcObject = stream;
      
      // 显示摄像头视频, 隐藏占位符
      cameraVideo.classList.remove('hidden');
      poseCanvas.classList.remove('hidden');
      cameraPlaceholder.classList.add('hidden');
      cameraStatus.classList.remove('hidden');
      
      // 更新状态
      isCameraActive = true;
      
      // 开始绘制摄像头画面
      drawCameraFeed();
      
      // 显示开始练习按钮
      startPracticeBtn.classList.remove('hidden');
      startCameraBtn.classList.add('hidden');
    } catch (err) {
      console.error('Error accessing camera:', err);
      showCameraError(err.message);
    }
  }
  
  // 停止摄像头函数
  function stopCamera() {
    if (mediaStream) {
      mediaStream.getTracks().forEach(track => track.stop());
      mediaStream = null;
    }
    
    cameraVideo.srcObject = null;
    isCameraActive = false;
    
    // 隐藏摄像头视频，显示占位符
    cameraVideo.classList.add('hidden');
    poseCanvas.classList.add('hidden');
    cameraPlaceholder.classList.remove('hidden');
    cameraStatus.classList.add('hidden');
    
    // 清除动画帧
    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId);
      animationFrameId = null;
    }
  }
  
  // 绘制摄像头画面函数
  function drawCameraFeed() {
    if (!isCameraActive) return;
    
    // 确保画布尺寸与视频一致
    if (cameraVideo.videoWidth > 0 && cameraVideo.videoHeight > 0) {
      poseCanvas.width = cameraVideo.videoWidth;
      poseCanvas.height = cameraVideo.videoHeight;
      
      // 绘制视频帧
      ctx.clearRect(0, 0, poseCanvas.width, poseCanvas.height);
      ctx.drawImage(cameraVideo, 0, 0, poseCanvas.width, poseCanvas.height);
      
      // 如果正在练习，绘制姿态检测效果
      if (isPracticing) {
        drawPoseDetection();
      } else {
        // 添加提示文字
        ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
        ctx.font = '16px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('点击"开始练习"按钮开始舞蹈模仿', poseCanvas.width / 2, poseCanvas.height - 30);
      }
    }
    
    // 持续更新摄像头画面
    animationFrameId = requestAnimationFrame(drawCameraFeed);
  }
  
  // 绘制姿态检测效果函数（模拟）
  function drawPoseDetection() {
    // 模拟生成17个关键点
    const points = generateRandomPoints(17);
    
    // 绘制关键点
    points.forEach(point => {
      ctx.beginPath();
      ctx.arc(point.x, point.y, 5, 0, 2 * Math.PI);
      ctx.fillStyle = 'red';
      ctx.fill();
      ctx.strokeStyle = 'white';
      ctx.lineWidth = 2;
      ctx.stroke();
    });
    
    // 绘制骨架连线（简化的骨架连接）
    const connections = [
      [0, 1], [1, 2], [2, 3], [3, 4], // 右侧手臂
      [0, 5], [5, 6], [6, 7], [7, 8], // 左侧手臂
      [0, 9], [9, 10], [10, 11], [11, 12], // 右侧腿
      [0, 13], [13, 14], [14, 15], [15, 16]  // 左侧腿
    ];
    
    connections.forEach(([i, j]) => {
      if (points[i] && points[j]) {
        ctx.beginPath();
        ctx.moveTo(points[i].x, points[i].y);
        ctx.lineTo(points[j].x, points[j].y);
        ctx.strokeStyle = 'yellow';
        ctx.lineWidth = 3;
        ctx.stroke();
      }
    });
  }
  
  // 生成随机关键点（用于模拟）
  function generateRandomPoints(count) {
    const points = [];
    for (let i = 0; i < count; i++) {
      points.push({
        x: Math.random() * poseCanvas.width,
        y: Math.random() * poseCanvas.height,
        confidence: 0.5 + Math.random() * 0.5
      });
    }
    return points;
  }
  
  // 显示摄像头错误信息
  function showCameraError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4';
    errorDiv.innerHTML = `
      <div class="bg-white rounded-xl p-6 max-w-md w-full text-center">
        <div class="text-red-500 text-4xl mb-4">
          <i class="fa-solid fa-video-slash"></i>
        </div>
        <h3 class="text-xl font-bold text-gray-800 mb-2">需要摄像头权限</h3>
        <p class="text-gray-600 mb-6">${message}</p>
        <div class="space-y-3">
          <button id="tryAgainBtn" class="w-full px-6 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors duration-300 font-medium">
            重试
          </button>
          <button id="checkBrowserBtn" class="w-full px-6 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors duration-300 font-medium">
            检查浏览器设置
          </button>
        </div>
      </div>
    `;
    document.body.appendChild(errorDiv);
    
    document.getElementById('tryAgainBtn').addEventListener('click', () => {
      document.body.removeChild(errorDiv);
      startCamera();
    });
    
    document.getElementById('checkBrowserBtn').addEventListener('click', () => {
      alert('请在浏览器设置中检查摄像头权限是否已启用，并确保没有其他应用正在使用摄像头。');
    });
  }
  
  // 开始练习函数
  function startPractice() {
    isPracticing = true;
    practiceTimeSeconds = 0;
    
    // 显示AI分析状态
    aiStatus.classList.remove('hidden');
    
    // 显示练习计时器
    practiceTimer.classList.remove('hidden');
    practiceProgress.classList.remove('hidden');
    
    // 清空反馈列表
    feedbackList.innerHTML = '';
    
    // 开始练习计时器
    practiceTimerInterval = setInterval(updatePracticeTimer, 1000);
    
    // 开始生成实时反馈
    generateRealtimeFeedback();
    
    // 显示结束练习按钮，隐藏开始练习按钮
    endPracticeBtn.classList.remove('hidden');
    startPracticeBtn.classList.add('hidden');
  }
  
  // 结束练习函数
  function endPractice() {
    isPracticing = false;
    
    // 隐藏AI分析状态
    aiStatus.classList.add('hidden');
    
    // 隐藏练习计时器
    practiceTimer.classList.add('hidden');
    
    // 清除计时器
    clearInterval(practiceTimerInterval);
    practiceTimerInterval = null;
    
    // 显示开始练习按钮，隐藏结束练习按钮
    startPracticeBtn.classList.remove('hidden');
    endPracticeBtn.classList.add('hidden');
    
    // 显示评分准备中的提示
    showScoringLoading();
  }
  
  // 更新练习计时器
  function updatePracticeTimer() {
    practiceTimeSeconds++;
    
    // 更新计时器显示
    const mins = Math.floor(practiceTimeSeconds / 60);
    const secs = practiceTimeSeconds % 60;
    practiceTimer.textContent = `${mins}:${secs < 10 ? '0' : ''}${secs}`;
    
    // 更新当前时间显示
    currentTime.textContent = practiceTimeSeconds;
  }
  
  // 生成实时反馈
  function generateRealtimeFeedback() {
    // 每隔2-3秒生成一条随机反馈
    const feedbackInterval = setInterval(() => {
      if (isPracticing) {
        const randomFeedback = feedbackMessages[Math.floor(Math.random() * feedbackMessages.length)];
        addFeedback(randomFeedback);
      } else {
        clearInterval(feedbackInterval);
      }
    }, 2000 + Math.random() * 1000);
  }
  
  // 添加反馈到列表
  function addFeedback(message) {
    const feedbackItem = document.createElement('div');
    feedbackItem.className = 'bg-gray-50 p-3 rounded-lg flex items-start animate-fadeIn';
    feedbackItem.innerHTML = `
      <i class="fa-solid fa-comment-dots text-red-500 mt-1 mr-3 flex-shrink-0"></i>
      <span class="text-gray-600">${message}</span>
    `;
    
    // 添加到反馈列表
    feedbackList.appendChild(feedbackItem);
    
    // 只保留最近5条反馈
    if (feedbackList.children.length > 5) {
      feedbackList.removeChild(feedbackList.firstChild);
    }
    
    // 滚动到底部
    feedbackList.scrollTop = feedbackList.scrollHeight;
  }
  
  // 显示评分准备中的提示
  function showScoringLoading() {
    const loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'fixed inset-0 bg-white/90 flex flex-col items-center justify-center z-50 p-4';
    loadingOverlay.innerHTML = `
      <div class="text-red-500 text-6xl mb-6">
        <i class="fa-solid fa-robot fa-spin"></i>
      </div>
      <h3 class="text-2xl font-bold text-gray-800 mb-2">AI正在评分中</h3>
      <p class="text-gray-600 mb-4">正在分析您的舞蹈动作，生成详细评分...</p>
      <div class="w-64 h-2 bg-gray-200 rounded-full overflow-hidden">
        <div class="h-full bg-gradient-to-r from-red-500 to-red-600 w-0 rounded-full" id="progressBar"></div>
      </div>
    `;
    document.body.appendChild(loadingOverlay);
    
    // 模拟进度条动画
    let progress = 0;
    const progressBar = document.getElementById('progressBar');
    const progressInterval = setInterval(() => {
      progress += Math.random() * 20;
      if (progress > 100) progress = 100;
      progressBar.style.width = `${progress}%`;
      
      if (progress === 100) {
        clearInterval(progressInterval);
        
        // 模拟延迟后跳转到结果页面
        setTimeout(() => {
          document.body.removeChild(loadingOverlay);
          // 跳转到结果页面
          window.location.href = `${window.location.origin}/community/dance-result/${window.location.pathname.split('/').pop()}`;
        }, 500);
      }
    }, 300);
  }
  
  // 搜索视频功能
  function searchVideosFunc() {
    const query = searchQuery.value.trim();
    if (!query) return;
    
    // 显示搜索结果区域
    searchResults.classList.remove('hidden');
    
    // 模拟搜索过程
    searchResults.innerHTML = `
      <div class="text-center py-4">
        <i class="fa-solid fa-spinner fa-spin text-gray-500 text-2xl"></i>
        <p class="text-gray-500 mt-2">搜索中...</p>
      </div>
    `;
    
    // 模拟搜索结果
    setTimeout(() => {
      const mockResults = [
        {
          id: '1',
          title: `${query} 教学视频 1`,
          videoUrl: 'https://example.com/video1.mp4'
        },
        {
          id: '2',
          title: `${query} 教学视频 2`,
          videoUrl: 'https://example.com/video2.mp4'
        },
        {
          id: '3',
          title: `${query} 教学视频 3`,
          videoUrl: 'https://example.com/video3.mp4'
        }
      ];
      
      // 生成搜索结果HTML
      let resultsHTML = '<h3 class="text-sm font-medium text-gray-700 mb-2">搜索结果:</h3>';
      mockResults.forEach(result => {
        resultsHTML += `
          <div class="bg-white border border-gray-200 rounded-lg p-2 mb-2 cursor-pointer hover:bg-gray-50 transition-colors">
            <p class="text-sm text-gray-800">${result.title}</p>
          </div>
        `;
      });
      
      searchResults.innerHTML = resultsHTML;
      
      // 添加点击事件监听
      searchResults.querySelectorAll('.bg-white').forEach((item, index) => {
        item.addEventListener('click', () => {
          // 在实际应用中，这里会更新当前舞蹈的视频URL
          console.log('Selected video:', mockResults[index].videoUrl);
          // 清空搜索结果
          searchResults.classList.add('hidden');
          searchQuery.value = '';
        });
      });
    }, 1500);
  }
  
  // 添加事件监听器
  startCameraBtn.addEventListener('click', startCamera);
  startPracticeBtn.addEventListener('click', startPractice);
  endPracticeBtn.addEventListener('click', endPractice);
  searchVideos.addEventListener('click', searchVideosFunc);
  
  // 清理资源
  window.addEventListener('beforeunload', () => {
    stopCamera();
    if (practiceTimerInterval) {
      clearInterval(practiceTimerInterval);
    }
    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId);
    }
  });
});