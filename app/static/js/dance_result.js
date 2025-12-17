// 舞蹈练习结果页面的JavaScript功能

document.addEventListener('DOMContentLoaded', function() {
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
      showCopySuccess();
    } catch (err) {
      console.error('复制失败:', err);
      alert('复制失败，请手动复制链接');
    }
  }
  
  // 显示复制成功提示
  function showCopySuccess() {
    // 保存原始按钮文本
    const originalText = copyBtn.textContent;
    
    // 更新按钮文本
    copyBtn.textContent = '已复制';
    copyBtn.classList.remove('bg-red-500');
    copyBtn.classList.add('bg-green-500');
    
    // 3秒后恢复原始状态
    setTimeout(() => {
      copyBtn.textContent = originalText;
      copyBtn.classList.remove('bg-green-500');
      copyBtn.classList.add('bg-red-500');
    }, 3000);
  }
  
  // 添加事件监听器
  shareBtn.addEventListener('click', showShareModal);
  closeShareModal.addEventListener('click', hideShareModal);
  copyLinkBtn.addEventListener('click', copyLinkToClipboard);
  copyBtn.addEventListener('click', copyLinkToClipboard);
  
  // 点击模态框外部关闭弹窗
  shareModal.addEventListener('click', function(e) {
    if (e.target === shareModal) {
      hideShareModal();
    }
  });
  
  // 按下Esc键关闭弹窗
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && !shareModal.classList.contains('hidden')) {
      hideShareModal();
    }
  });
  
  // 添加页面交互动效
  function addPageAnimations() {
    // 获取所有卡片元素
    const cards = document.querySelectorAll('.rounded-xl');
    
    // 添加淡入动画
    cards.forEach((card, index) => {
      // 初始状态
      card.style.opacity = '0';
      card.style.transform = 'translateY(20px)';
      card.style.transition = `opacity 0.5s ease ${index * 0.1}s, transform 0.5s ease ${index * 0.1}s`;
      
      // 延迟后添加动画类
      setTimeout(() => {
        card.style.opacity = '1';
        card.style.transform = 'translateY(0)';
      }, 100);
    });
    
    // 为评分数字添加动画
    const scoreNumbers = document.querySelectorAll('.text-2xl.font-semibold.text-red-600, .text-5xl.font-bold');
    scoreNumbers.forEach(number => {
      const target = parseFloat(number.textContent);
      let current = 0;
      const increment = target / 50;
      
      // 使用requestAnimationFrame实现平滑动画
      function animateScore() {
        current += increment;
        if (current < target) {
          number.textContent = current.toFixed(1);
          requestAnimationFrame(animateScore);
        } else {
          number.textContent = target;
        }
      }
      
      // 延迟开始动画
      setTimeout(animateScore, 500);
    });
  }
  
  // 初始化页面动画
  addPageAnimations();
  
  // 社交媒体分享功能（模拟）
  function initSocialSharing() {
    // 获取所有社交媒体分享按钮
    const socialButtons = shareModal.querySelectorAll('.grid-cols-3 button');
    
    socialButtons.forEach(button => {
      button.addEventListener('click', function() {
        const platform = this.querySelector('span').textContent;
        
        // 模拟分享操作
        console.log(`分享到${platform}: ${shareLink.value}`);
        
        // 显示分享成功提示
        alert(`已分享到${platform}`);
        
        // 隐藏分享弹窗
        hideShareModal();
      });
    });
  }
  
  // 初始化社交媒体分享功能
  initSocialSharing();
  
  // 添加按钮悬停效果
  function addButtonHoverEffects() {
    const buttons = document.querySelectorAll('button, a');
    
    buttons.forEach(button => {
      button.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-2px)';
        this.style.transition = 'transform 0.2s ease';
      });
      
      button.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
      });
    });
  }
  
  // 初始化按钮悬停效果
  addButtonHoverEffects();
});