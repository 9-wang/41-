// 舞蹈选择页面的JavaScript功能

document.addEventListener('DOMContentLoaded', function() {
  // 获取DOM元素
  const searchTerm = document.getElementById('searchTerm');
  const category = document.getElementById('category');
  const difficulty = document.getElementById('difficulty');
  const danceList = document.getElementById('danceList');
  const emptyState = document.getElementById('emptyState');
  const resetFilters = document.getElementById('resetFilters');
  
  // 保存原始舞蹈卡片数据
  const originalDanceCards = Array.from(danceList.children);
  
  // 筛选舞蹈函数
  function filterDances() {
    const searchValue = searchTerm.value.toLowerCase();
    const categoryValue = category.value;
    const difficultyValue = difficulty.value;
    
    let filteredCount = 0;
    
    // 遍历所有舞蹈卡片，根据筛选条件显示或隐藏
    originalDanceCards.forEach(card => {
      const title = card.querySelector('h3').textContent.toLowerCase();
      const description = card.querySelector('p').textContent.toLowerCase();
      const cardCategory = card.querySelector('.text-gray-500').textContent;
      const cardDifficulty = card.querySelector('.rounded-full').textContent;
      
      // 映射中文难度到英文
      const difficultyMap = {
        '简单': 'easy',
        '中等': 'medium',
        '困难': 'hard'
      };
      
      const mappedDifficulty = difficultyMap[cardDifficulty];
      
      // 检查是否匹配所有筛选条件
      const matchesSearch = title.includes(searchValue) || description.includes(searchValue);
      const matchesCategory = categoryValue === 'all' || cardCategory === categoryValue;
      const matchesDifficulty = difficultyValue === 'all' || mappedDifficulty === difficultyValue;
      
      if (matchesSearch && matchesCategory && matchesDifficulty) {
        card.style.display = 'block';
        filteredCount++;
      } else {
        card.style.display = 'none';
      }
    });
    
    // 显示或隐藏空状态
    if (filteredCount === 0) {
      danceList.style.display = 'none';
      emptyState.style.display = 'flex';
    } else {
      danceList.style.display = 'grid';
      emptyState.style.display = 'none';
    }
  }
  
  // 重置筛选条件函数
  function resetAllFilters() {
    searchTerm.value = '';
    category.value = 'all';
    difficulty.value = 'all';
    filterDances();
  }
  
  // 添加事件监听器
  searchTerm.addEventListener('input', filterDances);
  category.addEventListener('change', filterDances);
  difficulty.addEventListener('change', filterDances);
  resetFilters.addEventListener('click', resetAllFilters);
  
  // 初始化筛选
  filterDances();
  
  // 添加卡片悬停效果
  originalDanceCards.forEach(card => {
    card.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-5px)';
      this.style.transition = 'transform 0.3s ease, box-shadow 0.3s ease';
      this.style.boxShadow = '0 10px 20px rgba(0, 0, 0, 0.1)';
    });
    
    card.addEventListener('mouseleave', function() {
      this.style.transform = 'translateY(0)';
      this.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
    });
  });
  
  // 添加平滑滚动效果
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      document.querySelector(this.getAttribute('href')).scrollIntoView({
        behavior: 'smooth'
      });
    });
  });
});