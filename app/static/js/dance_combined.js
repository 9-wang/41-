// 舞蹈相关页面的合并JavaScript功能

// 舞蹈选择页面功能
document.addEventListener('DOMContentLoaded', function() {
  // 舞蹈选择页面的搜索和筛选功能
  if (document.getElementById('searchTerm')) {
    const searchTerm = document.getElementById('searchTerm');
    const danceCards = document.querySelectorAll('.dance-card');
    
    searchTerm.addEventListener('input', function(e) {
      const searchValue = e.target.value.toLowerCase();
      
      danceCards.forEach(card => {
        const title = card.querySelector('h3').textContent.toLowerCase();
        const description = card.querySelector('p').textContent.toLowerCase();
        
        if (title.includes(searchValue) || description.includes(searchValue)) {
          card.style.display = 'block';
        } else {
          card.style.display = 'none';
        }
      });
    });
    
    // 添加卡片悬停效果
    danceCards.forEach(card => {
      card.addEventListener('mouseenter', function() {
        this.classList.add('hover:shadow-xl');
      });
      
      card.addEventListener('mouseleave', function() {
        this.classList.remove('hover:shadow-xl');
      });
    });
  }
  
  // 舞蹈练习页面功能
  if (document.getElementById('startCameraBtn')) {
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
    
    // 画布上下文
    const ctx = poseCanvas.getContext('2d');
    
    // 状态变量
    let isCameraActive = false;
    let isPracticing = false;
    let practiceTimeSeconds = 0;
    let practiceTimerInterval = null;
    let animationFrameId = null;
    let mediaStream = null;
    
    // 初始化视频元素尺寸
    function initializeCanvas() {
      if (cameraVideo && poseCanvas) {
        poseCanvas.width = cameraVideo.offsetWidth;
        poseCanvas.height = cameraVideo.offsetHeight;
      }
    }
    
    // 启动摄像头
    async function startCamera() {
      try {
        mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
        cameraVideo.srcObject = mediaStream;
        
        // 等待视频加载完成
        await new Promise(resolve => {
          cameraVideo.onloadedmetadata = resolve;
        });
        
        cameraVideo.play();
        isCameraActive = true;
        
        // 更新UI
        cameraPlaceholder.style.display = 'none';
        cameraVideo.style.display = 'block';
        poseCanvas.style.display = 'block';
        cameraStatus.textContent = '摄像头已启动';
        cameraStatus.className = 'text-green-600';
        
        // 初始化画布尺寸
        initializeCanvas();
        
        // 开始绘制骨架
        drawPoseSkeleton();
      } catch (error) {
        console.error('启动摄像头失败:', error);
        cameraStatus.textContent = '无法启动摄像头';
        cameraStatus.className = 'text-red-600';
      }
    }
    
    // 停止摄像头
    function stopCamera() {
      if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
        mediaStream = null;
        cameraVideo.srcObject = null;
        isCameraActive = false;
        
        // 更新UI
        cameraVideo.style.display = 'none';
        poseCanvas.style.display = 'none';
        cameraPlaceholder.style.display = 'flex';
        cameraStatus.textContent = '摄像头未启动';
        cameraStatus.className = 'text-gray-500';
      }
    }
    
    // 绘制骨架
    function drawPoseSkeleton() {
      if (!isCameraActive || !cameraVideo) return;
      
      // 清空画布
      ctx.clearRect(0, 0, poseCanvas.width, poseCanvas.height);
      
      // 在实际应用中，这里应该使用MediaPipe Pose或其他姿态检测库来获取骨架数据
      // 目前只是绘制一个简单的示例
      ctx.strokeStyle = '#FF0000';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(poseCanvas.width / 2, poseCanvas.height / 2, 20, 0, Math.PI * 2);
      ctx.stroke();
      
      // 继续绘制
      animationFrameId = requestAnimationFrame(drawPoseSkeleton);
    }
    
    // 开始练习
    function startPractice() {
      if (!isCameraActive) {
        alert('请先启动摄像头');
        return;
      }
      
      isPracticing = true;
      practiceTimeSeconds = 0;
      
      // 更新UI
      startPracticeBtn.disabled = true;
      endPracticeBtn.disabled = false;
      aiStatus.textContent = 'AI正在分析...';
      aiStatus.className = 'text-blue-600';
      
      // 启动计时器
      practiceTimerInterval = setInterval(updatePracticeTimer, 1000);
      
      // 开始AI分析（模拟）
      startAIAnalysis();
    }
    
    // 结束练习
    function endPractice() {
      isPracticing = false;
      
      // 清除计时器
      if (practiceTimerInterval) {
        clearInterval(practiceTimerInterval);
        practiceTimerInterval = null;
      }
      
      // 更新UI
      startPracticeBtn.disabled = false;
      endPracticeBtn.disabled = true;
      aiStatus.textContent = 'AI分析已结束';
      aiStatus.className = 'text-green-600';
    }
    
    // 更新练习计时器
    function updatePracticeTimer() {
      practiceTimeSeconds++;
      
      // 格式化时间
      const minutes = Math.floor(practiceTimeSeconds / 60);
      const seconds = practiceTimeSeconds % 60;
      const formattedTime = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
      
      // 更新UI
      practiceTimer.textContent = formattedTime;
      
      // 更新进度条
      // 假设练习时长为60秒
      const progress = Math.min((practiceTimeSeconds / 60) * 100, 100);
      practiceProgress.style.width = `${progress}%`;
      
      // 如果达到最大时长，自动结束练习
      if (practiceTimeSeconds >= 60) {
        endPractice();
      }
    }
    
    // 开始AI分析（模拟）
    function startAIAnalysis() {
      // 模拟AI分析，每隔2秒生成一条反馈
      const analysisInterval = setInterval(() => {
        if (!isPracticing) {
          clearInterval(analysisInterval);
          return;
        }
        
        // 生成随机反馈
        const feedbacks = [
          '手臂抬得更高一些',
          '脚步要跟上节奏',
          '身体保持平衡',
          '手势更自然一些',
          '转身时要平稳',
          '表情更生动一些'
        ];
        
        const randomFeedback = feedbacks[Math.floor(Math.random() * feedbacks.length)];
        addFeedback(randomFeedback);
      }, 2000);
    }
    
    // 添加反馈
    function addFeedback(feedback) {
      if (!feedbackList) return;
      
      const feedbackItem = document.createElement('div');
      feedbackItem.className = 'bg-blue-50 p-3 rounded-lg mb-2 flex items-start';
      
      const feedbackIcon = document.createElement('i');
      feedbackIcon.className = 'fa-solid fa-info-circle text-blue-500 mt-0.5 mr-3 flex-shrink-0';
      
      const feedbackText = document.createElement('p');
      feedbackText.className = 'text-gray-700';
      feedbackText.textContent = feedback;
      
      feedbackItem.appendChild(feedbackIcon);
      feedbackItem.appendChild(feedbackText);
      
      // 添加到反馈列表
      feedbackList.appendChild(feedbackItem);
      
      // 滚动到最新反馈
      feedbackItem.scrollIntoView({ behavior: 'smooth' });
    }
    
    // 事件监听器
    startCameraBtn.addEventListener('click', startCamera);
    startPracticeBtn.addEventListener('click', startPractice);
    endPracticeBtn.addEventListener('click', endPractice);
    
    // 页面卸载时清理资源
    window.addEventListener('beforeunload', function() {
      stopCamera();
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
      }
      if (practiceTimerInterval) {
        clearInterval(practiceTimerInterval);
      }
    });
    
    // 窗口大小改变时重新初始化画布
    window.addEventListener('resize', initializeCanvas);
  }
  
  // 舞蹈结果页面功能
  if (document.getElementById('shareBtn')) {
    // 获取DOM元素
    const shareBtn = document.getElementById('shareBtn');
    const shareModal = document.getElementById('shareModal');
    const closeShareModal = document.getElementById('closeShareModal');
    const copyLinkBtn = document.getElementById('copyLinkBtn');
    const copyBtn = document.getElementById('copyBtn');
    const shareLink = document.getElementById('shareLink');
    
    // 显示分享弹窗
    function showShareModal() {
      shareModal.classList.remove('hidden');
      document.body.style.overflow = 'hidden';
    }
    
    // 隐藏分享弹窗
    function hideShareModal() {
      shareModal.classList.add('hidden');
      document.body.style.overflow = '';
    }
    
    // 复制链接到剪贴板
    async function copyLinkToClipboard() {
      try {
        // 复制链接
        await navigator.clipboard.writeText(shareLink.value);
        
        // 显示复制成功提示
        const copyBtnText = copyBtn.textContent;
        copyBtn.textContent = '已复制';
        copyBtn.classList.add('bg-green-500');
        
        // 恢复原状态
        setTimeout(() => {
          copyBtn.textContent = copyBtnText;
          copyBtn.classList.remove('bg-green-500');
        }, 2000);
      } catch (error) {
        console.error('复制链接失败:', error);
        alert('复制链接失败，请手动复制');
      }
    }
    
    // 事件监听器
    shareBtn.addEventListener('click', showShareModal);
    closeShareModal.addEventListener('click', hideShareModal);
    copyLinkBtn.addEventListener('click', copyLinkToClipboard);
    copyBtn.addEventListener('click', copyLinkToClipboard);
    
    // 点击弹窗外部关闭弹窗
    shareModal.addEventListener('click', function(e) {
      if (e.target === shareModal) {
        hideShareModal();
      }
    });
    
    // ESC键关闭弹窗
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && !shareModal.classList.contains('hidden')) {
        hideShareModal();
      }
    });
  }
  
  // 舞蹈选择页面的卡片动画
  const danceCards = document.querySelectorAll('.dance-card');
  danceCards.forEach((card, index) => {
    card.style.animationDelay = `${index * 0.1}s`;
  });
  
  // 添加通用的平滑滚动效果
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      
      const targetId = this.getAttribute('href');
      const targetElement = document.querySelector(targetId);
      
      if (targetElement) {
        targetElement.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });
  
  // 添加通用的按钮悬停效果
  const buttons = document.querySelectorAll('button, .btn, a[href]');
  buttons.forEach(button => {
    button.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-2px)';
    });
    
    button.addEventListener('mouseleave', function() {
      this.style.transform = 'translateY(0)';
    });
  });
  
  // 雷达图绘制函数
  function drawRadarChart() {
    const canvas = document.getElementById('radarChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // 设置画布尺寸
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    
    // 清除画布
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // 评分数据（从页面数据中获取）
    const data = [
      { name: '动作准确性', value: parseFloat(canvas.dataset.accuracyScore || '0') },
      { name: '节奏把握', value: parseFloat(canvas.dataset.rhythmScore || '0') },
      { name: '表现力', value: parseFloat(canvas.dataset.expressionScore || '0') },
      { name: '完整性', value: parseFloat(canvas.dataset.completenessScore || '0') },
      { name: '协调性', value: parseFloat(canvas.dataset.coordinationScore || '0') }
    ];
    
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(centerX, centerY) - 40;
    
    // 绘制网格
    ctx.strokeStyle = '#e2e8f0';
    ctx.lineWidth = 1;
    ctx.fillStyle = '#f8fafc';
    
    for (let i = 1; i <= 5; i++) {
      const r = radius * i / 5;
      ctx.beginPath();
      ctx.arc(centerX, centerY, r, 0, 2 * Math.PI);
      ctx.fill();
      ctx.stroke();
    }
    
    // 绘制轴线
    ctx.strokeStyle = '#cbd5e1';
    ctx.lineWidth = 1;
    
    data.forEach((item, index) => {
      const angle = (2 * Math.PI * index) / data.length - Math.PI / 2;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);
      
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.lineTo(x, y);
      ctx.stroke();
    });
    
    // 绘制数据区域
    ctx.beginPath();
    ctx.strokeStyle = '#ef4444';
    ctx.fillStyle = 'rgba(239, 68, 68, 0.3)';
    ctx.lineWidth = 2;
    
    data.forEach((item, index) => {
      const angle = (2 * Math.PI * index) / data.length - Math.PI / 2;
      const r = radius * item.value / 100;
      const x = centerX + r * Math.cos(angle);
      const y = centerY + r * Math.sin(angle);
      
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    
    // 绘制数据点
    ctx.fillStyle = '#ef4444';
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 2;
    
    data.forEach((item, index) => {
      const angle = (2 * Math.PI * index) / data.length - Math.PI / 2;
      const r = radius * item.value / 100;
      const x = centerX + r * Math.cos(angle);
      const y = centerY + r * Math.sin(angle);
      
      ctx.beginPath();
      ctx.arc(x, y, 6, 0, 2 * Math.PI);
      ctx.fill();
      ctx.stroke();
    });
    
    // 绘制标签
    ctx.fillStyle = '#64748b';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    
    data.forEach((item, index) => {
      const angle = (2 * Math.PI * index) / data.length - Math.PI / 2;
      const r = radius + 20;
      const x = centerX + r * Math.cos(angle);
      const y = centerY + r * Math.sin(angle);
      
      ctx.fillText(item.name, x, y);
    });
    
    // 绘制数值
    ctx.fillStyle = '#ef4444';
    ctx.font = '14px Arial';
    ctx.fontWeight = 'bold';
    
    data.forEach((item, index) => {
      const angle = (2 * Math.PI * index) / data.length - Math.PI / 2;
      const r = radius * item.value / 100;
      const x = centerX + r * Math.cos(angle);
      const y = centerY + r * Math.sin(angle);
      
      ctx.fillText(item.value, x, y);
    });
  }
  
  // 页面加载时绘制雷达图
  if (document.getElementById('radarChart')) {
    window.addEventListener('load', drawRadarChart);
    // 窗口大小改变时重绘雷达图
    window.addEventListener('resize', drawRadarChart);
  }
});