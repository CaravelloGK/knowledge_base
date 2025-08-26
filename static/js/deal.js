function createProgressCircle() {
    // Создаем элементы
    const overlay = document.createElement('div');
    const progressContainer = document.createElement('div');
    const progressCircle = document.createElement('div');
    const progressText = document.createElement('div');
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    const circleBg = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    const circleProgress = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
  
    // Стили для оверлея
    Object.assign(overlay.style, {
      position: 'fixed',
      top: '0',
      left: '0',
      width: '100%',
      height: '100%',
      backgroundColor: 'rgba(0, 0, 0, 0.7)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      zIndex: '9999',
      transition: 'opacity 0.3s'
    });
  
    // Стили для контейнера
    Object.assign(progressContainer.style, {
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: '20px'
    });
  
    // Настройки SVG
    const size = 120;
    const strokeWidth = 8;
    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
  
    svg.setAttribute('width', size);
    svg.setAttribute('height', size);
    svg.setAttribute('viewBox', `0 0 ${size} ${size}`);
    svg.style.transform = 'rotate(-90deg)';
  
    // Фоновый круг
    circleBg.setAttribute('cx', size / 2);
    circleBg.setAttribute('cy', size / 2);
    circleBg.setAttribute('r', radius);
    circleBg.setAttribute('fill', 'none');
    circleBg.setAttribute('stroke', '#e0e0e0');
    circleBg.setAttribute('stroke-width', strokeWidth);
  
    // Прогресс круг
    circleProgress.setAttribute('cx', size / 2);
    circleProgress.setAttribute('cy', size / 2);
    circleProgress.setAttribute('r', radius);
    circleProgress.setAttribute('fill', 'none');
    circleProgress.setAttribute('stroke', '#4285F4');
    circleProgress.setAttribute('stroke-width', strokeWidth);
    circleProgress.setAttribute('stroke-linecap', 'round');
    circleProgress.setAttribute('stroke-dasharray', circumference);
    circleProgress.setAttribute('stroke-dashoffset', circumference);
  
    // Текст
    Object.assign(progressText.style, {
      color: 'white',
      fontSize: '24px',
      fontWeight: 'bold'
    });
    progressText.textContent = 'Загрузка...';
  
    // Сборка элементов
    svg.appendChild(circleBg);
    svg.appendChild(circleProgress);
    progressCircle.appendChild(svg);
    progressContainer.appendChild(progressCircle);
    progressContainer.appendChild(progressText);
    overlay.appendChild(progressContainer);
  
    // Анимация вращения
    let progress = 0;
    let animationId = null;
    let lastTimestamp = 0;
    const animationDuration = 2000; // Полный цикл анимации
  
    const animate = (timestamp) => {
      if (!lastTimestamp) lastTimestamp = timestamp;
      const delta = timestamp - lastTimestamp;
  
      progress = (progress + delta / animationDuration) % 1;
      const dashOffset = circumference - (progress * circumference);
      circleProgress.setAttribute('stroke-dashoffset', dashOffset);
  
      lastTimestamp = timestamp;
      animationId = requestAnimationFrame(animate);
    };
  
    return {
      show: () => {
        document.body.appendChild(overlay);
        animationId = requestAnimationFrame(animate);
      },
      hide: () => {
        if (animationId) cancelAnimationFrame(animationId);
        overlay.style.opacity = '0';
        setTimeout(() => {
          if (overlay.parentNode) {
            document.body.removeChild(overlay);
          }
        }, 300);
      },
      setText: (text) => {
        progressText.textContent = text;
      }
    };
  }
  
  // Глобальная переменная для хранения инстанса
  let progressCircleInstance = null;
  
  window.showProgressCircle = () => {
    if (!progressCircleInstance) {
      progressCircleInstance = createProgressCircle();
    }
    progressCircleInstance.show();
    return progressCircleInstance;
  };
  
  window.hideProgressCircle = () => {
    if (progressCircleInstance) {
      progressCircleInstance.hide();
      progressCircleInstance = null;
    }
  };