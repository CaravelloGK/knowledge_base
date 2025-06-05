document.addEventListener('DOMContentLoaded', function() {
  // -----------------------
  // Переключение темы + иконка
  // -----------------------
  initThemeSwitcher();

  // -----------------------
  // Прогрессивная загрузка для legal entities
  // -----------------------
  initProgressiveLoading();

  // -----------------------
  // Инициализация поиска и фильтрации
  // -----------------------
  initEntitySearch();
});

/* =====================================================================
   ПЕРЕКЛЮЧЕНИЕ ТЕМЫ
   ===================================================================== */
function initThemeSwitcher() {
  const toggleBtn = document.getElementById('theme-toggle');
  const iconEl = document.getElementById('theme-icon');
  const root = document.documentElement;

  if (!toggleBtn) return;

  const isMainPage = root.classList.contains('main-page');
  if (isMainPage) {
    root.classList.remove('dark-theme');
  } else {
    const theme = localStorage.getItem('theme');
    if (theme === 'dark') {
      root.classList.add('dark-theme');
    } else {
      root.classList.remove('dark-theme');
    }
  }

  const isDarkNow = root.classList.contains('dark-theme');
  setThemeIcon(isDarkNow);

  toggleBtn.addEventListener('click', function () {
    root.classList.add('no-transitions');
    const willBeDark = !root.classList.contains('dark-theme');
    root.classList.toggle('dark-theme', willBeDark);
    localStorage.setItem('theme', willBeDark ? 'dark' : 'light');
    setThemeIcon(willBeDark);
    root.offsetHeight;
    setTimeout(() => {
      root.classList.remove('no-transitions');
    }, 0);
  });

  function setThemeIcon(dark) {
    if (!iconEl) return;
    iconEl.classList.toggle('bi-sun', dark);
    iconEl.classList.toggle('bi-moon-stars', !dark);
  }
}

/* =====================================================================
   ПОИСК ПО ЮРИДИЧЕСКИМ ЛИЦАМ
   ===================================================================== */
function initEntitySearch() {
  const searchInput = document.querySelector('input[name="query"]');
  const entityItems = document.querySelectorAll('.entity-item');
  const refreshBtn = document.getElementById('refresh-btn');

  if (!searchInput || !entityItems.length) return;

  // Поиск по мере ввода
  searchInput.addEventListener('input', function() {
    const searchQuery = this.value.trim().toLowerCase();
    
    entityItems.forEach(item => {
      const name = item.querySelector('.entity-name')?.textContent?.toLowerCase() || '';
      const inn = item.querySelector('.entity-inn')?.textContent?.toLowerCase() || '';
      const ogrn = item.querySelector('.entity-ogrn')?.textContent?.toLowerCase() || '';
      
      const matches = name.includes(searchQuery) || 
                     inn.includes(searchQuery) || 
                     ogrn.includes(searchQuery);
      
      item.style.display = matches ? '' : 'none';
    });
  });

  // Кнопка обновить - очистить поиск
  if (refreshBtn) {
    refreshBtn.addEventListener('click', function() {
      searchInput.value = '';
      entityItems.forEach(item => {
        item.style.display = '';
      });
    });
  }
}

/* =====================================================================
   ПРОГРЕССИВНАЯ ЗАГРУЗКА LEGAL ENTITIES
   ===================================================================== */
function initProgressiveLoading() {
  // Проверяем, что мы на странице legal_opin и есть контейнер
  const entitiesContainer = document.getElementById('entities-container');
  const loadingIndicator = document.getElementById('loading-indicator');
  const dataElement = document.getElementById('legal-entities-data');
  
  if (!entitiesContainer || !dataElement) {
    return;
  }

  // Читаем данные из data-атрибутов
  window.legalEntitiesData = {
    totalCount: parseInt(dataElement.dataset.totalCount) || 0,
    loadedCount: parseInt(dataElement.dataset.loadedCount) || 0,
    hasMore: dataElement.dataset.hasMore === 'true'
  };

  let isLoading = false;
  let isFullyLoaded = false;
  
  // Показать/скрыть индикатор загрузки
  function showLoadingIndicator() {
    if (loadingIndicator) {
      loadingIndicator.style.display = 'block';
    }
  }

  function hideLoadingIndicator() {
    if (loadingIndicator) {
      loadingIndicator.style.display = 'none';
    }
  }

  // Загрузка дополнительных данных
  async function loadMoreEntities() {
    if (isLoading || isFullyLoaded) return;
    
    isLoading = true;
    showLoadingIndicator();

    try {
      const offset = window.legalEntitiesData.loadedCount;
      const response = await fetch(`/legal_opin/api/load-more/?offset=${offset}&limit=50`);
      
      if (!response.ok) {
        throw new Error('API endpoint не найден');
      }

      const data = await response.json();
      
      // Добавляем новые элементы в таблицу
      data.entities.forEach(entity => {
        const entityRow = createEntityRow(entity);
        entitiesContainer.appendChild(entityRow);
      });

      // Обновляем счетчики
      window.legalEntitiesData.loadedCount += data.entities.length;
      window.legalEntitiesData.hasMore = data.has_more;
      
      if (!data.has_more) {
        isFullyLoaded = true;
      }

      // Переинициализируем поиск для новых элементов
      initEntitySearch();

    } catch (error) {
      console.warn('API endpoint для прогрессивной загрузки еще не создан:', error);
      // Fallback: считаем что все данные уже загружены
      isFullyLoaded = true;
      window.legalEntitiesData.hasMore = false;
    } finally {
      isLoading = false;
      hideLoadingIndicator();
    }
  }

  // Создание HTML элемента строки таблицы
  function createEntityRow(entity) {
    const row = document.createElement('tr');
    row.className = 'entity-item';
    row.style.borderBottom = '1px solid #f0f0f0';
    
    // Добавляем data-атрибуты для поиска
    row.setAttribute('data-name', entity.name.toLowerCase());
    row.setAttribute('data-inn', entity.inn);
    row.setAttribute('data-ogrn', entity.ogrn);
    row.setAttribute('data-update-date', entity.update_date);
    
    row.innerHTML = `
      <td class="py-3 px-3">${window.legalEntitiesData.loadedCount + 1}</td>
      <td class="py-3 px-3">
        <a href="${entity.url}" class="text-decoration-none text-primary entity-name">${entity.name}</a>
      </td>
      <td class="py-3 px-3 entity-inn">${entity.inn}</td>
      <td class="py-3 px-3 entity-ogrn">${entity.ogrn}</td>
      <td class="py-3 px-3 entity-date">${entity.formatted_date}</td>
    `;
    
    return row;
  }

  // Запуск фоновой загрузки
  function startBackgroundLoading() {
    // Небольшая задержка, чтобы страница успела отрендериться
    setTimeout(() => {
      if (window.legalEntitiesData.hasMore) {
        loadMoreEntities();
      } else {
        console.log('🚀 Прогрессивная загрузка инициализирована для legal entities');
        console.log('📊 Загружено записей:', window.legalEntitiesData.loadedCount);
        console.log('📈 Всего записей:', window.legalEntitiesData.totalCount);
      }
    }, 500);
  }

  // Публичные функции для проверки состояния загрузки
  window.isLegalEntitiesFullyLoaded = function() {
    return isFullyLoaded;
  };

  window.ensureLegalEntitiesFullyLoaded = function() {
    return new Promise((resolve) => {
      if (isFullyLoaded) {
        resolve();
        return;
      }
      
      showLoadingIndicator();
      
      const checkLoaded = () => {
        if (isFullyLoaded) {
          hideLoadingIndicator();
          resolve();
        } else {
          setTimeout(checkLoaded, 100);
        }
      };
      
      checkLoaded();
    });
  };

  // Инициализация
  startBackgroundLoading();
}
