// 舞蹈数据（模拟数据，实际应用中从API获取）
const danceData = [
  {
    id: 1,
    title: "藏族锅庄舞",
    ethnicity: "藏族",
    difficulty: "初级",
    difficultyLevel: "low",
    videoUrl: "https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=0&mute=1", // 使用YouTube视频作为占位符
    description: "适合初学者的藏族锅庄舞，动作简单易学，富有民族特色",
    duration: 180
  },
  {
    id: 2,
    title: "蒙古族筷子舞",
    ethnicity: "蒙古族",
    difficulty: "中级",
    difficultyLevel: "medium",
    videoUrl: "https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=0&mute=1", // 使用YouTube视频作为占位符
    description: "具有浓郁蒙古族特色的筷子舞，节奏明快，动作流畅",
    duration: 240
  },
  {
    id: 3,
    title: "维吾尔族手鼓舞",
    ethnicity: "维吾尔族",
    difficulty: "高级",
    difficultyLevel: "high",
    videoUrl: "https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=0&mute=1", // 使用YouTube视频作为占位符
    description: "富有活力的维吾尔族手鼓舞，包含旋转和跳跃动作",
    duration: 300
  },
  {
    id: 4,
    title: "汉族扇舞",
    ethnicity: "汉族",
    difficulty: "中级",
    difficultyLevel: "medium",
    videoUrl: "https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=0&mute=1", // 使用YouTube视频作为占位符
    description: "优雅的汉族扇舞，动作柔美，富有古典韵味",
    duration: 210
  },
  {
    id: 5,
    title: "傣族孔雀舞",
    ethnicity: "傣族",
    difficulty: "高级",
    difficultyLevel: "high",
    videoUrl: "https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=0&mute=1", // 使用YouTube视频作为占位符
    description: "惟妙惟肖的傣族孔雀舞，动作细腻，表现力强",
    duration: 270
  },
  {
    id: 6,
    title: "彝族跳月",
    ethnicity: "彝族",
    difficulty: "初级",
    difficultyLevel: "low",
    videoUrl: "/static/videos/dance/yi-dance.mp4",
    description: "欢快的彝族跳月舞蹈，适合群体参与",
    duration: 150
  }
];

// 全局变量
let currentDance = null;
let isPlaying = false;
let isCameraOn = false;
let videoElement = null;
let cameraFeed = null;
let poseCanvas = null;
let poseContext = null;
let threeDCanvas = null;
let scene = null;
let camera = null;
let renderer = null;
let dancer = null;
let animationId = null;
let poseDetector = null;
let actionSequence = [];
let currentFrame = 0;
let scoreInterval = null;

// 练习计时相关变量
let isPracticing = false;
let practiceTime = 0;
let practiceTimer = null;
let practiceStartTime = null;

// 初始化页面
document.addEventListener('DOMContentLoaded', function() {
  initializePage();
});

// 初始化页面函数
function initializePage() {
  // 初始化DOM元素
  initializeElements();
  
  // 渲染舞蹈列表
  renderDanceList(danceData);
  
  // 初始化事件监听
  initializeEventListeners();
  
  // 初始化视频播放器
  initializeVideoPlayer();
  
  // 初始化3D场景
  initializeThreeDScene();
  
  // 初始化姿态检测器
  initializePoseDetector();
  
  // 默认选择第一个舞蹈
  if (danceData.length > 0) {
    selectDance(danceData[0]);
  }
}

// 初始化DOM元素
function initializeElements() {
  videoElement = document.getElementById('dance-video');
  cameraFeed = document.getElementById('camera-feed');
  poseCanvas = document.getElementById('pose-canvas');
  poseContext = poseCanvas.getContext('2d');
  threeDCanvas = document.getElementById('three-d-canvas');
}

// 初始化事件监听
function initializeEventListeners() {
  // 视频控制按钮
  document.getElementById('play-pause-btn').addEventListener('click', togglePlayPause);
  document.getElementById('rewind-btn').addEventListener('click', rewindVideo);
  document.getElementById('forward-btn').addEventListener('click', forwardVideo);
  document.getElementById('speed-select').addEventListener('change', changePlaybackSpeed);
  
  // 摄像头控制
  document.getElementById('toggle-camera').addEventListener('click', toggleCamera);
  
  // 3D小人控制
  document.getElementById('reset-小人').addEventListener('click', resetDancer);
  document.getElementById('小人-style').addEventListener('change', changeDancerStyle);
  
  // 过滤控制
  document.getElementById('difficulty-filter').addEventListener('change', applyFilters);
  document.getElementById('ethnicity-filter').addEventListener('change', applyFilters);
  document.getElementById('search-input').addEventListener('input', applyFilters);
  
  // 练习控制
  document.getElementById('start-practice')?.addEventListener('click', startPractice);
  document.getElementById('stop-practice')?.addEventListener('click', stopPractice);
  
  // 视频时间更新
  videoElement.addEventListener('timeupdate', updateVideoTime);
  videoElement.addEventListener('loadedmetadata', updateVideoDuration);
}

// 渲染舞蹈列表
function renderDanceList(dances) {
  const danceList = document.getElementById('dance-list');
  danceList.innerHTML = '';
  
  dances.forEach((dance, index) => {
    const danceCard = createDanceCard(dance);
    
    // 添加Framer Motion动画
    const cardContainer = document.createElement('div');
    cardContainer.className = 'dance-card-container';
    cardContainer.style.opacity = '0';
    cardContainer.style.transform = 'translateY(20px)';
    cardContainer.appendChild(danceCard);
    danceList.appendChild(cardContainer);
    
    // 使用Framer Motion添加动画效果
    if (window.motion) {
      window.motion.animate(cardContainer, {
        opacity: 1,
        y: 0
      }, {
        duration: 0.5,
        delay: index * 0.1,
        ease: "easeOut"
      });
    } else {
      // 备用动画，使用CSS动画
      setTimeout(() => {
        cardContainer.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
        cardContainer.style.opacity = '1';
        cardContainer.style.transform = 'translateY(0)';
      }, index * 100);
    }
  });
}

// 创建舞蹈卡片
function createDanceCard(dance) {
  // 格式化时长
  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };
  
  // 获取难度对应的颜色和文本
  const getDifficultyInfo = (difficulty) => {
    switch (difficulty) {
      case '初级':
        return { color: 'bg-green-100 text-green-800', text: '初级' };
      case '中级':
        return { color: 'bg-yellow-100 text-yellow-800', text: '中级' };
      case '高级':
        return { color: 'bg-red-100 text-red-800', text: '高级' };
      default:
        return { color: 'bg-gray-100 text-gray-800', text: '未知' };
    }
  };
  
  const difficultyInfo = getDifficultyInfo(dance.difficulty);
  
  const card = document.createElement('div');
  card.className = 'bg-white rounded-xl shadow-md overflow-hidden border border-gray-100 hover:shadow-lg transition-shadow duration-300 cursor-pointer';
  card.dataset.id = dance.id;
  
  card.innerHTML = `
    <div class="relative h-48 overflow-hidden">
      <div class="w-full h-full bg-gradient-to-br from-[#E74C3C] to-[#C0392B] flex items-center justify-center text-white text-5xl">
        <i class="fas fa-music"></i>
      </div>
      <div class="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent flex items-end p-4">
        <h3 class="text-white font-bold text-xl">${dance.title}</h3>
      </div>
      <div class="absolute top-3 right-3 px-3 py-1 rounded-full text-xs font-medium bg-black/50 text-white">
        ${formatDuration(dance.duration)}
      </div>
    </div>
    
    <div class="p-5">
      <div class="flex items-center mb-3">
        <span class="text-gray-500 text-sm flex items-center">
          <i class="fa-solid fa-flag mr-1"></i> ${dance.ethnicity}
        </span>
        <span class="mx-2 text-gray-300">|</span>
        <span class="px-2 py-1 rounded-full text-xs font-medium ${difficultyInfo.color}">
          ${difficultyInfo.text}
        </span>
      </div>
      
      <p class="text-gray-600 text-sm mb-4 line-clamp-2">${dance.description}</p>
      
      <div class="w-full text-center py-2 bg-[#E74C3C] text-white rounded-lg hover:bg-[#C0392B] transition-colors duration-300 font-medium">
        开始模仿 <i class="fa-solid fa-play ml-1"></i>
      </div>
    </div>
  `;
  
  card.addEventListener('click', () => selectDance(dance));
  
  return card;
}

// 选择舞蹈
function selectDance(dance) {
  // 更新当前舞蹈
  currentDance = dance;
  
  // 更新视频源
  videoElement.src = dance.videoUrl;
  
  // 检查视频加载状态
  videoElement.load();
  
  // 更新UI状态
  updateDanceSelection(dance.id);
  
  // 重置3D小人
  resetDancer();
  
  // 获取动作序列
  fetchActionSequence(dance.id);
  
  // 重置评分
  resetScores();
}

// 更新舞蹈选择状态
function updateDanceSelection(danceId) {
  // 移除所有选中状态
  document.querySelectorAll('.dance-card').forEach(card => {
    card.classList.remove('selected');
  });
  
  // 添加当前选中状态
  const selectedCard = document.querySelector(`[data-id="${danceId}"]`);
  if (selectedCard) {
    selectedCard.classList.add('selected');
  }
}

// 应用过滤条件
function applyFilters() {
  const difficultyFilter = document.getElementById('difficulty-filter').value;
  const ethnicityFilter = document.getElementById('ethnicity-filter').value;
  const searchTerm = document.getElementById('search-input').value.toLowerCase();
  
  let filteredDances = danceData;
  
  // 应用搜索过滤
  if (searchTerm) {
    filteredDances = filteredDances.filter(dance => {
      return dance.title.toLowerCase().includes(searchTerm) || 
             dance.description.toLowerCase().includes(searchTerm) ||
             dance.ethnicity.toLowerCase().includes(searchTerm);
    });
  }
  
  // 应用难度过滤
  if (difficultyFilter) {
    filteredDances = filteredDances.filter(dance => dance.difficulty === difficultyFilter);
  }
  
  // 应用民族过滤
  if (ethnicityFilter) {
    filteredDances = filteredDances.filter(dance => dance.ethnicity === ethnicityFilter);
  }
  
  // 重新渲染舞蹈列表
  renderDanceList(filteredDances);
}

// 初始化视频播放器
function initializeVideoPlayer() {
  // 设置默认播放速度
  videoElement.playbackRate = 1;
  
  // 添加视频加载错误处理
  videoElement.addEventListener('error', function(e) {
    console.error('视频加载失败:', e);
    // 显示友好的错误信息
    const errorMessage = document.createElement('div');
    errorMessage.className = 'video-error-message';
    errorMessage.innerHTML = '<p>视频加载失败，请检查网络连接或稍后重试</p><p>您可以继续使用摄像头进行动作捕捉和评分功能</p>';
    errorMessage.style.cssText = `
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background-color: rgba(0, 0, 0, 0.8);
      color: white;
      padding: 20px;
      border-radius: 8px;
      text-align: center;
      z-index: 10;
      max-width: 80%;
    `;
    
    // 检查是否已存在错误信息
    const existingError = videoElement.parentElement.querySelector('.video-error-message');
    if (!existingError) {
      videoElement.parentElement.style.position = 'relative';
      videoElement.parentElement.appendChild(errorMessage);
    }
  });
}

// 切换播放/暂停
function togglePlayPause() {
  const btn = document.getElementById('play-pause-btn');
  const icon = btn.querySelector('i');
  
  if (isPlaying) {
    videoElement.pause();
    isPlaying = false;
    icon.classList.remove('fa-pause');
    icon.classList.add('fa-play');
    stopScoreUpdate();
  } else {
    videoElement.play();
    isPlaying = true;
    icon.classList.remove('fa-play');
    icon.classList.add('fa-pause');
    startScoreUpdate();
  }
}

// 快退视频
function rewindVideo() {
  // 检查视频是否已加载完成
  if (isNaN(videoElement.duration) || !isFinite(videoElement.duration)) {
    return;
  }
  
  // 确保currentTime是有限值
  const currentTime = isFinite(videoElement.currentTime) ? videoElement.currentTime : 0;
  
  try {
    videoElement.currentTime = Math.max(0, currentTime - 10);
  } catch (error) {
    console.error('设置视频当前时间失败:', error);
  }
}

// 快进视频
function forwardVideo() {
  // 检查视频是否已加载完成
  if (isNaN(videoElement.duration) || !isFinite(videoElement.duration)) {
    return;
  }
  
  // 确保currentTime是有限值
  const currentTime = isFinite(videoElement.currentTime) ? videoElement.currentTime : 0;
  
  try {
    videoElement.currentTime = Math.min(videoElement.duration, currentTime + 10);
  } catch (error) {
    console.error('设置视频当前时间失败:', error);
  }
}

// 改变播放速度
function changePlaybackSpeed() {
  const speed = parseFloat(document.getElementById('speed-select').value);
  videoElement.playbackRate = speed;
}

// 更新视频时间
function updateVideoTime() {
  const currentTime = formatTime(videoElement.currentTime);
  document.getElementById('current-time').textContent = currentTime;
  
  // 更新3D小人动作
  if (isPlaying && actionSequence.length > 0) {
    updateDancerPose();
  }
}

// 更新视频总时长
function updateVideoDuration() {
  const totalTime = formatTime(videoElement.duration);
  document.getElementById('total-time').textContent = totalTime;
}

// 格式化时间
function formatTime(seconds) {
  if (isNaN(seconds)) return '00:00';
  
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// 切换摄像头
function toggleCamera() {
  if (isCameraOn) {
    stopCamera();
  } else {
    startCamera();
  }
}

// 启动摄像头
async function startCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    cameraFeed.srcObject = stream;
    isCameraOn = true;
    
    // 启动姿态检测
    startPoseDetection();
    
    // 更新按钮状态
    const btn = document.getElementById('toggle-camera');
    btn.classList.add('active');
  } catch (error) {
    console.error('无法访问摄像头:', error);
    alert('无法访问摄像头，请确保已授予摄像头权限');
  }
}

// 停止摄像头
function stopCamera() {
  if (cameraFeed.srcObject) {
    const tracks = cameraFeed.srcObject.getTracks();
    tracks.forEach(track => track.stop());
    cameraFeed.srcObject = null;
    isCameraOn = false;
    
    // 停止姿态检测
    stopPoseDetection();
    
    // 清空画布
    poseContext.clearRect(0, 0, poseCanvas.width, poseCanvas.height);
    
    // 更新按钮状态
    const btn = document.getElementById('toggle-camera');
    btn.classList.remove('active');
  }
}

// 初始化姿态检测器
async function initializePoseDetector() {
  try {
    // 检查必要的全局对象是否存在
    if (typeof tf === 'undefined' || typeof poseDetection === 'undefined') {
      console.error('姿态检测所需的库未正确加载');
      return;
    }
    
    // 检查createDetector方法是否存在
    if (typeof poseDetection.createDetector !== 'function') {
      console.error('poseDetection.createDetector不是一个函数，可能是库版本不兼容');
      return;
    }
    
    // 等待TensorFlow.js加载
    await tf.setBackend('webgl');
    await tf.ready();
    
    // 检查SupportedModels.MediapipePose是否存在
    if (typeof poseDetection.SupportedModels === 'undefined' || typeof poseDetection.SupportedModels.MediapipePose === 'undefined') {
      console.error('poseDetection.SupportedModels.MediapipePose未定义');
      return;
    }
    
    // 创建姿态检测器
    poseDetector = await poseDetection.createDetector(poseDetection.SupportedModels.MediapipePose, {
      runtime: 'tfjs',
      modelType: 'lite',
      solutionPath: 'https://cdn.jsdelivr.net/npm/@mediapipe/pose@0.5.1675469404/'
    });
    
    // 设置画布尺寸
    resizePoseCanvas();
    window.addEventListener('resize', resizePoseCanvas);
    
    console.log('姿态检测器初始化成功');
  } catch (error) {
    console.error('姿态检测器初始化失败:', error);
    // 即使初始化失败，也不要中断其他功能
  }
}

// 调整姿态检测画布尺寸
function resizePoseCanvas() {
  const container = cameraFeed.parentElement;
  poseCanvas.width = container.clientWidth;
  poseCanvas.height = container.clientHeight;
}

// 启动姿态检测
function startPoseDetection() {
  if (poseDetector) {
    detectPose();
  }
}

// 停止姿态检测
function stopPoseDetection() {
  if (animationId) {
    cancelAnimationFrame(animationId);
    animationId = null;
  }
}

// 姿态检测
async function detectPose() {
  if (!isCameraOn) return;
  
  try {
    // 检测姿态
    const poses = await poseDetector.estimatePoses(cameraFeed, {
      flipHorizontal: true
    });
    
    // 绘制姿态
    drawPose(poses[0]);
    
    // 更新姿态统计
    updatePoseStats(poses[0]);
    
    // 继续检测
    animationId = requestAnimationFrame(detectPose);
  } catch (error) {
    console.error('姿态检测失败:', error);
    animationId = requestAnimationFrame(detectPose);
  }
}

// 绘制姿态
function drawPose(pose) {
  if (!pose) {
    poseContext.clearRect(0, 0, poseCanvas.width, poseCanvas.height);
    return;
  }
  
  // 清空画布
  poseContext.clearRect(0, 0, poseCanvas.width, poseCanvas.height);
  
  // 绘制关键点
  drawKeypoints(pose.keypoints);
  
  // 绘制骨架
  drawSkeleton(pose.keypoints);
}

// 绘制关键点
function drawKeypoints(keypoints) {
  if (!keypoints) return;
  
  poseContext.fillStyle = '#667eea';
  poseContext.strokeStyle = '#ffffff';
  poseContext.lineWidth = 2;
  
  keypoints.forEach(keypoint => {
    if (keypoint.score > 0.5) {
      const { x, y } = keypoint;
      poseContext.beginPath();
      poseContext.arc(x, y, 5, 0, 2 * Math.PI);
      poseContext.fill();
      poseContext.stroke();
    }
  });
}

// 绘制骨架
function drawSkeleton(keypoints) {
  if (!keypoints) return;
  
  poseContext.strokeStyle = '#667eea';
  poseContext.lineWidth = 3;
  
  // 定义骨架连接
  const connections = [
    [0, 1], [1, 2], [2, 3], [3, 7],
    [0, 4], [4, 5], [5, 6], [6, 8],
    [9, 10],
    [11, 12], [11, 13], [13, 15], [12, 14], [14, 16],
    [11, 23], [12, 24], [23, 24],
    [23, 25], [25, 27], [27, 29], [29, 31],
    [24, 26], [26, 28], [28, 30], [30, 32]
  ];
  
  connections.forEach(connection => {
    const [startIdx, endIdx] = connection;
    const startPoint = keypoints[startIdx];
    const endPoint = keypoints[endIdx];
    
    if (startPoint.score > 0.5 && endPoint.score > 0.5) {
      poseContext.beginPath();
      poseContext.moveTo(startPoint.x, startPoint.y);
      poseContext.lineTo(endPoint.x, endPoint.y);
      poseContext.stroke();
    }
  });
}

// 更新姿态统计
function updatePoseStats(pose) {
  if (!pose) {
    document.getElementById('pose-confidence').textContent = '0%';
    document.getElementById('keypoint-count').textContent = '0/33';
    return;
  }
  
  // 计算姿态置信度
  const confidence = Math.round(pose.score * 100);
  document.getElementById('pose-confidence').textContent = `${confidence}%`;
  
  // 计算检测到的关键点数量
  const detectedKeypoints = pose.keypoints.filter(keypoint => keypoint.score > 0.5).length;
  document.getElementById('keypoint-count').textContent = `${detectedKeypoints}/33`;
}

// 初始化3D场景
function initializeThreeDScene() {
  // 创建场景
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf5f5f5);
  
  // 创建相机
  camera = new THREE.PerspectiveCamera(
    75,
    threeDCanvas.clientWidth / threeDCanvas.clientHeight,
    0.1,
    1000
  );
  camera.position.z = 5;
  
  // 创建渲染器
  renderer = new THREE.WebGLRenderer({
    canvas: threeDCanvas,
    antialias: true,
    alpha: true
  });
  renderer.setSize(threeDCanvas.clientWidth, threeDCanvas.clientHeight);
  renderer.setPixelRatio(window.devicePixelRatio);
  
  // 添加灯光
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
  scene.add(ambientLight);
  
  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
  directionalLight.position.set(1, 1, 1);
  scene.add(directionalLight);
  
  // 创建3D小人
  createDancer();
  
  // 开始渲染循环
  animate();
  
  // 监听窗口大小变化
  window.addEventListener('resize', resizeThreeDCanvas);
  
  // 隐藏加载覆盖层
  setTimeout(() => {
    const loadingOverlay = document.getElementById('loading-overlay');
    loadingOverlay.classList.add('hidden');
  }, 1000);
}

// 调整3D画布尺寸
function resizeThreeDCanvas() {
  camera.aspect = threeDCanvas.clientWidth / threeDCanvas.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(threeDCanvas.clientWidth, threeDCanvas.clientHeight);
}

// 创建3D小人
function createDancer() {
  // 创建一个简单的3D小人模型（使用基本几何体组合）
  dancer = new THREE.Group();
  
  // 头部
  const headGeometry = new THREE.SphereGeometry(0.3, 32, 32);
  const headMaterial = new THREE.MeshStandardMaterial({ color: 0xffdbac });
  const head = new THREE.Mesh(headGeometry, headMaterial);
  head.position.y = 1.5;
  dancer.add(head);
  
  // 身体
  const bodyGeometry = new THREE.CylinderGeometry(0.3, 0.4, 1, 32);
  const bodyMaterial = new THREE.MeshStandardMaterial({ color: 0x667eea });
  const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
  body.position.y = 0.8;
  dancer.add(body);
  
  // 四肢
  const limbGeometry = new THREE.CylinderGeometry(0.08, 0.08, 0.8, 16);
  
  // 左臂
  const leftArm = new THREE.Mesh(limbGeometry, bodyMaterial);
  leftArm.position.set(-0.4, 1.2, 0);
  leftArm.rotation.z = Math.PI / 4;
  dancer.add(leftArm);
  
  // 右臂
  const rightArm = new THREE.Mesh(limbGeometry, bodyMaterial);
  rightArm.position.set(0.4, 1.2, 0);
  rightArm.rotation.z = -Math.PI / 4;
  dancer.add(rightArm);
  
  // 左腿
  const leftLeg = new THREE.Mesh(limbGeometry, bodyMaterial);
  leftLeg.position.set(-0.2, 0.2, 0);
  leftLeg.rotation.z = Math.PI / 6;
  dancer.add(leftLeg);
  
  // 右腿
  const rightLeg = new THREE.Mesh(limbGeometry, bodyMaterial);
  rightLeg.position.set(0.2, 0.2, 0);
  rightLeg.rotation.z = -Math.PI / 6;
  dancer.add(rightLeg);
  
  scene.add(dancer);
}

// 动画循环
function animate() {
  requestAnimationFrame(animate);
  
  // 更新3D小人姿态
  updateDancerPose();
  
  renderer.render(scene, camera);
}

// 更新3D小人姿态
function updateDancerPose() {
  if (!dancer || actionSequence.length === 0) return;
  
  // 获取当前帧的动作
  const currentAction = actionSequence[currentFrame];
  if (currentAction) {
    // 更新小人位置
    dancer.position.x = currentAction.position.x * 0.01;
    dancer.position.y = currentAction.position.y * 0.01;
    dancer.position.z = currentAction.position.z * 0.01;
    
    // 更新小人旋转
    dancer.rotation.x = currentAction.rotation.x * Math.PI / 180;
    dancer.rotation.y = currentAction.rotation.y * Math.PI / 180;
    dancer.rotation.z = currentAction.rotation.z * Math.PI / 180;
    
    // 更新当前帧
    currentFrame = (currentFrame + 1) % actionSequence.length;
  }
}

// 重置3D小人
function resetDancer() {
  if (dancer) {
    dancer.position.set(0, 0, 0);
    dancer.rotation.set(0, 0, 0);
  }
  currentFrame = 0;
}

// 改变小人风格
function changeDancerStyle() {
  const style = document.getElementById('小人-style').value;
  // 这里可以根据风格切换不同的3D模型
  console.log('切换小人风格:', style);
}

// 获取动作序列
async function fetchActionSequence(danceId) {
  try {
    // 调用后端API获取动作序列
    const response = await fetch(`/api/dance/generate_actions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        dance_type: currentDance.ethnicity,
        difficulty: currentDance.difficulty,
        duration: currentDance.duration
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      actionSequence = data.action_sequence;
      currentFrame = 0;
    } else {
      // 使用模拟动作序列
      generateMockActionSequence();
    }
  } catch (error) {
    console.error('获取动作序列失败:', error);
    // 使用模拟动作序列
    generateMockActionSequence();
  }
}

// 生成模拟动作序列
function generateMockActionSequence() {
  actionSequence = [];
  const frameCount = 200;
  
  for (let i = 0; i < frameCount; i++) {
    actionSequence.push({
      frame: i,
      action: 'dance',
      position: {
        x: Math.sin(i * 0.1) * 20,
        y: Math.cos(i * 0.1) * 5,
        z: Math.sin(i * 0.05) * 10
      },
      rotation: {
        x: Math.sin(i * 0.1) * 10,
        y: Math.sin(i * 0.05) * 360,
        z: Math.cos(i * 0.1) * 10
      },
      timestamp: i * 0.08
    });
  }
}

// 开始评分更新
function startScoreUpdate() {
  if (scoreInterval) {
    clearInterval(scoreInterval);
  }
  
  // 每1秒更新一次评分
  scoreInterval = setInterval(updateScores, 1000);
}

// 停止评分更新
function stopScoreUpdate() {
  if (scoreInterval) {
    clearInterval(scoreInterval);
    scoreInterval = null;
  }
}

// 更新评分
async function updateScores() {
  try {
    // 调用后端API获取评分
    const response = await fetch(`/api/dance/score`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        video_url: currentDance.videoUrl,
        dance_id: currentDance.id
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      displayScores(data.score_result);
    } else {
      // 使用模拟评分
      displayMockScores();
    }
  } catch (error) {
    console.error('获取评分失败:', error);
    // 使用模拟评分
    displayMockScores();
  }
}

// 显示评分
function displayScores(scoreResult) {
  // 更新总分
  document.getElementById('total-score').textContent = scoreResult.overall;
  
  // 更新各项评分
  updateScoreBar('accuracy', scoreResult.dimensions.accuracy);
  updateScoreBar('rhythm', scoreResult.dimensions.rhythm);
  updateScoreBar('expression', scoreResult.dimensions.expression);
  updateScoreBar('completeness', scoreResult.dimensions.completeness);
  
  // 更新反馈建议
  updateFeedback(scoreResult.feedback);
}

// 显示模拟评分
function displayMockScores() {
  // 生成随机评分
  const overall = (Math.random() * 20 + 80).toFixed(1);
  const accuracy = (Math.random() * 20 + 80).toFixed(1);
  const rhythm = (Math.random() * 20 + 80).toFixed(1);
  const expression = (Math.random() * 20 + 80).toFixed(1);
  const completeness = (Math.random() * 20 + 80).toFixed(1);
  
  // 更新总分
  document.getElementById('total-score').textContent = overall;
  
  // 更新各项评分
  updateScoreBar('accuracy', accuracy);
  updateScoreBar('rhythm', rhythm);
  updateScoreBar('expression', expression);
  updateScoreBar('completeness', completeness);
  
  // 更新模拟反馈建议
  const mockFeedback = [
    "动作整体流畅，但手臂动作可以更舒展",
    "节奏感良好，建议在跳跃动作时加强爆发力",
    "表情生动，继续保持",
    "动作完成度高，细节处理到位"
  ];
  updateFeedback(mockFeedback);
}

// 更新评分条
function updateScoreBar(type, score) {
  const progressBar = document.getElementById(`${type}-progress`);
  const scoreValue = document.getElementById(`${type}-score`);
  
  const percentage = (score / 100) * 100;
  progressBar.style.width = `${percentage}%`;
  scoreValue.textContent = score;
}

// 更新反馈建议
function updateFeedback(feedback) {
  const feedbackList = document.getElementById('feedback-list');
  feedbackList.innerHTML = '';
  
  if (feedback.length > 0) {
    feedback.forEach((item, index) => {
      const li = document.createElement('li');
      li.className = 'flex items-start p-3 mb-2 bg-white rounded-lg shadow-sm border-l-4 border-[#E74C3C]';
      li.innerHTML = `
        <div class="text-green-500 mt-0.5 mr-2">
          <i class="fa-solid fa-circle-info text-lg"></i>
        </div>
        <div class="flex-1">
          <p class="text-gray-700 text-sm">${item}</p>
          <div class="flex items-center justify-end mt-1">
            <span class="text-xs text-gray-500">${getCurrentTime()}</span>
          </div>
        </div>
      `;
      
      // 添加进入动画
      li.style.opacity = '0';
      li.style.transform = 'translateX(-10px)';
      feedbackList.appendChild(li);
      
      // 动画效果
      setTimeout(() => {
        li.style.transition = 'opacity 0.3s ease-out, transform 0.3s ease-out';
        li.style.opacity = '1';
        li.style.transform = 'translateX(0)';
      }, index * 100);
    });
  } else {
    const li = document.createElement('li');
    li.className = 'flex items-start p-3 bg-white rounded-lg shadow-sm border-l-4 border-gray-300';
    li.innerHTML = `
      <div class="text-gray-500 mt-0.5 mr-2">
        <i class="fa-solid fa-circle-info text-lg"></i>
      </div>
      <div class="flex-1">
        <p class="text-gray-700 text-sm">正在分析您的动作，请稍候...</p>
        <div class="flex items-center justify-end mt-1">
          <span class="text-xs text-gray-500">${getCurrentTime()}</span>
        </div>
      </div>
    `;
    feedbackList.appendChild(li);
  }
}

// 获取当前时间
function getCurrentTime() {
  const now = new Date();
  const hours = now.getHours().toString().padStart(2, '0');
  const minutes = now.getMinutes().toString().padStart(2, '0');
  return `${hours}:${minutes}`;
}

// 重置评分
function resetScores() {
  // 重置总分
  document.getElementById('total-score').textContent = '0.0';
  
  // 重置各项评分
  updateScoreBar('accuracy', 0);
  updateScoreBar('rhythm', 0);
  updateScoreBar('expression', 0);
  updateScoreBar('completeness', 0);
  
  // 重置反馈建议
  const feedbackList = document.getElementById('feedback-list');
  feedbackList.innerHTML = `
    <li class="flex items-start">
      <div class="text-green-500 mt-1 mr-2">
        <i class="fa-solid fa-circle-info"></i>
      </div>
      <p class="text-gray-700 text-sm">请站在摄像头前，开始跳舞</p>
    </li>
  `;
}

// 开始练习
function startPractice() {
  if (isPracticing) return;
  
  isPracticing = true;
  practiceStartTime = Date.now();
  
  // 更新练习状态
  updatePracticeStatus('练习中');
  
  // 启动练习计时器
  practiceTimer = setInterval(() => {
    practiceTime = Math.floor((Date.now() - practiceStartTime) / 1000);
    updatePracticeTime();
  }, 1000);
  
  // 自动启动摄像头
  if (!isCameraOn) {
    startCamera();
  }
  
  // 自动开始播放视频
  if (!isPlaying) {
    togglePlayPause();
  }
}

// 停止练习
function stopPractice() {
  if (!isPracticing) return;
  
  isPracticing = false;
  
  // 停止练习计时器
  clearInterval(practiceTimer);
  practiceTimer = null;
  
  // 更新练习状态
  updatePracticeStatus('准备就绪');
  
  // 重置练习时间
  practiceTime = 0;
  practiceStartTime = null;
  updatePracticeTime();
  
  // 停止播放视频
  if (isPlaying) {
    togglePlayPause();
  }
}

// 更新练习时间显示
function updatePracticeTime() {
  const minutes = Math.floor(practiceTime / 60).toString().padStart(2, '0');
  const seconds = (practiceTime % 60).toString().padStart(2, '0');
  const timeString = `${minutes}:${seconds}`;
  
  const practiceTimeElement = document.getElementById('practice-time');
  if (practiceTimeElement) {
    practiceTimeElement.textContent = timeString;
  }
}

// 更新练习状态
function updatePracticeStatus(status) {
  const practiceStatusElement = document.getElementById('practice-status');
  if (practiceStatusElement) {
    practiceStatusElement.textContent = status;
  }
}

// 工具函数
function getRandomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}