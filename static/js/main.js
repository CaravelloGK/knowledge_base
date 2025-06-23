document.addEventListener('DOMContentLoaded', function() {
  // -----------------------
  // Переключение темы + иконка
  // -----------------------
  initThemeSwitcher();
  initCustomDropdowns();

  // -----------------------
  // Прогрессивная загрузка (НОВОЕ!)
  // -----------------------
  initProgressiveLoading();

  // -----------------------
  // Инициализация Flatpickr
  // -----------------------
  initDatePickers();

  // -----------------------
  // Инициализация Фильтрации
  // -----------------------
  initNewsFilters();

  // --------------------------------------------------
  // Поиск и сортировка рубрик (универсальная функция, т.к. на разных страницах разные ID у поля поиска)
  // --------------------------------------------------
  // Вызов для list.html (где простой поиск по рубрикам)
  initRubricSearchAndSort({
    searchInputSelector: '#rubricSearchInput',    // как в list
    containerSelector: '.rubrics-scrollable'
  });

  // Вызов для review_multiple_form и review_form
  initRubricSearchAndSort({
    searchInputSelector: '#rubricSearchInputCreate',
    containerSelector: '#rubricContainerCreate'
  });

  // ----------------------------------------
  // Поиск по обзорам (это на review_multiple)
  // ----------------------------------------
  initReviewSearch({
    searchInputSelector: '.rubric-search-container input[name="query"]',
    itemSelector: '.preview-item'
  });

  // ----------------------------------------
  // Кастомная валидация форм
  // ----------------------------------------
  initBootstrapValidation();   // Bootstrap валидация для форм с классом need-validation (email+textarea проверки)
  // Для обзоров на review_multiple_form.html, где надо выбирать несколько новостей
  initCheckboxValidation({
    formSelector: '#send-form',
    checkboxesContainer: '#reviewContainerCreate',
    invalidBlockSelector: '#reviewFormGroup'
  });
  // Для чекбоксов "Рубрики" на review_form.html, где надо проверять рубрики
  initCheckboxValidation({
    formSelector: '.needs-validation',
    checkboxesContainer: '#rubricContainerCreate',
    invalidBlockSelector: '#rubricFormGroup'
  });

  // ----------------------------------------
  // "Выбрать все" чекбоксы (review_multiple_form)
  // ----------------------------------------
  initSelectAll({
    selectAllSelector: '#select-all-box',
    checkboxesContainer: '#reviewContainerCreate',
    invalidBlockSelector: '#reviewFormGroup'
  });

  // -------------------------------------------------------
  // Popover предпросмотр обзора (review_multiple_form)
  // -------------------------------------------------------
  initReviewPreviewPopover({
    previewItemSelector: '.preview-item',
    fetchUrlTemplate: '/reviews/review-preview/{id}/'
    // {id} будет заменён на значение чекбокса value
  });

  // ----------------------------------------
  // Стрелочки вверх-вниз в <select>'ах (review_form)
  // ----------------------------------------
  initSelectArrows(['#id_powers', '#id_category']);

  // ----------------------------------------
  // Авто-расширение textarea (review_form)
  // ----------------------------------------
  autoExpandTextarea('#id_name');

  // ----------------------------------------
  // Логика "Статус -> Показать/скрыть дату статуса" (review_form)
  // ----------------------------------------
  initStatusDateVisibility({
    statusSelector: '#id_powers',
    dateGroupSelector: '#powerDateGroup',
    dateInputSelector: '#id_power_date'
  });
});

/* =====================================================================
   ИНИЦИАЛИЗАЦИЯ FLATPICKR
   (Везде, где есть календарь)
   ===================================================================== */
function initDatePickers() {
  // Flatpickr для периода (list, review_multiple_form)
  if (typeof flatpickr !== 'undefined') {
    flatpickr('.period-field', {
      dateFormat: 'Y-m-d',
      altInput: true,
      altFormat: 'd.m.Y',
      locale: 'ru',
      allowInput: true,
      clickOpens: true
    });

  // Flatpickr для review_form
    // Поле "Дата статуса"
    if (document.querySelector('#id_power_date')) {
      flatpickr('#id_power_date', {
        dateFormat: 'd.m.Y',
        locale: 'ru',
        allowInput: true
      });
    }

    // Поле "Дата публикации"
    if (document.querySelector('#id_publication_date')) {
      flatpickr('#id_publication_date', {
        dateFormat: 'd.m.Y',
        locale: 'ru',
        allowInput: true
      });
    }
  }
}

/* =====================================================================
   2) ПОИСК И СОРТИРОВКА РУБРИК
   (list, review_multiple_form, review_form)
   ===================================================================== */
function initRubricSearchAndSort({ searchInputSelector, containerSelector }) {
  const searchInput = document.querySelector(searchInputSelector);
  const container = document.querySelector(containerSelector);

  if (!searchInput || !container) return;

  // Функция поиска
  searchInput.addEventListener('input', function() {
    const filter = searchInput.value.toLowerCase();
    const rubricItems = container.querySelectorAll('.form-check, .rubric-item-create');
    rubricItems.forEach(item => {
      const label = item.querySelector('.form-check-label, label');
      if (label && label.textContent.toLowerCase().includes(filter)) {
        item.style.display = '';
      } else {
        item.style.display = 'none';
      }
    });
  });

  // Функция сортировки (отмеченные вверх, затем по алфавиту)
  function sortRubrics() {
    const rubricItems = Array.from(container.querySelectorAll('.form-check, .rubric-item-create'));
    rubricItems.sort((a, b) => {
      const aChecked = a.querySelector('input[type="checkbox"]')?.checked;
      const bChecked = b.querySelector('input[type="checkbox"]')?.checked;
      // Сначала идут отмеченные
      if (aChecked !== bChecked) {
        return aChecked ? -1 : 1;
      }
      // Если одинаково отмечены или нет – сортируем по алфавиту
      const labelA = a.querySelector('.form-check-label, label')?.textContent.trim().toLowerCase() || '';
      const labelB = b.querySelector('.form-check-label, label')?.textContent.trim().toLowerCase() || '';
      return labelA.localeCompare(labelB);
    });
    // Пересобираем контейнер
    container.innerHTML = '';
    rubricItems.forEach(el => container.appendChild(el));
  }

  // Сортировка при загрузке
  sortRubrics();

  // Пересортировка при изменении чекбоксов
  container.addEventListener('change', event => {
    if (event.target.type === 'checkbox') {
      sortRubrics();
    }
  });
}

/* =====================================================================
   3) ПОИСК ПО ОБЗОРАМ
   (review_multiple_form)
   ===================================================================== */
function initReviewSearch({ searchInputSelector, itemSelector }) {
  const searchInput = document.querySelector(searchInputSelector);
  const items = document.querySelectorAll(itemSelector);
  if (!searchInput || !items.length) return;

  searchInput.addEventListener('input', function () {
    const filter = searchInput.value.toLowerCase();
    items.forEach(item => {
      const label = item.querySelector('label');
      const text = label?.textContent?.toLowerCase() || '';
      if (text.includes(filter)) {
        item.style.setProperty('display', '', 'important');
      } else {
        item.style.setProperty('display', 'none', 'important');
      }
    });
  });
}

/* =====================================================================
   4) БАЗОВАЯ ВАЛИДАЦИЯ ФОРМ (Bootstrap 5 "needs-validation")
   (review_multiple_form, review_form, review_mail)
   ===================================================================== */
function initBootstrapValidation() {
  const forms = document.querySelectorAll('.needs-validation');
  forms.forEach(form => {
    form.addEventListener('submit', function(event) {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      form.classList.add('was-validated');
    }, false);
  });
}

/* =====================================================================
   5) КАСТОМНАЯ ВАЛИДАЦИЯ ЧЕКБОКСОВ
   (review_form, review_multiple_form)
   ===================================================================== */
function initCheckboxValidation({ formSelector, checkboxesContainer, invalidBlockSelector }) {
  const form = document.querySelector(formSelector);
  const container = document.querySelector(checkboxesContainer);
  const invalidBlock = document.querySelector(invalidBlockSelector);
  if (!form || !container || !invalidBlock) return;

  const checkboxes = container.querySelectorAll('input[type="checkbox"]');
  if (!checkboxes.length) return;

  let formWasSubmitted = false;

  function isAnyChecked() {
    return Array.from(checkboxes).some(cb => cb.checked);
  }

  // При сабмите формы
  form.addEventListener('submit', function(e) {
    formWasSubmitted = true;
    // Если не отмечено ни одного чекбокса – не даём отправить
    if (!isAnyChecked()) {
      e.preventDefault();
      e.stopPropagation();
      invalidBlock.classList.add('is-invalid');
      const errorMsg = invalidBlock.querySelector('.invalid-feedback');
      if (errorMsg) errorMsg.style.display = 'block';
    } else {
      invalidBlock.classList.remove('is-invalid');
      const errorMsg = invalidBlock.querySelector('.invalid-feedback');
      if (errorMsg) errorMsg.style.display = 'none';
    }
  });

  // Если пользователь меняет состояние чекбоксов
  checkboxes.forEach(cb => {
    cb.addEventListener('change', function() {
      if (!formWasSubmitted) return;
      if (isAnyChecked()) {
        invalidBlock.classList.remove('is-invalid');
        const errorMsg = invalidBlock.querySelector('.invalid-feedback');
        if (errorMsg) errorMsg.style.display = 'none';
      } else {
        invalidBlock.classList.add('is-invalid');
        const errorMsg = invalidBlock.querySelector('.invalid-feedback');
        if (errorMsg) errorMsg.style.display = 'block';
      }
    });
  });
}

/* =====================================================================
   6) "ВЫБРАТЬ ВСЕ" ЧЕКБОКС
   (review_multiple_form)
   ===================================================================== */
function initSelectAll({ selectAllSelector, checkboxesContainer, invalidBlockSelector }) {
  const selectAllBox = document.querySelector(selectAllSelector);
  const container = document.querySelector(checkboxesContainer);
  const invalidBlock = document.querySelector(invalidBlockSelector);
  if (!selectAllBox || !container || !invalidBlock) return;

  const checkboxes = container.querySelectorAll('input[type="checkbox"]');
  let formWasSubmitted = false;

  // Чтобы синхронизироваться с общей валидацией, перехватываем submit, если он есть
  const form = selectAllBox.closest('form');
  if (form) {
    form.addEventListener('submit', () => {
      formWasSubmitted = true;
    });
  }

  selectAllBox.addEventListener('change', function() {
    const shouldCheck = this.checked;
    checkboxes.forEach(cb => {
      cb.checked = shouldCheck;
    });

    if (formWasSubmitted) {
      const isAnyChecked = Array.from(checkboxes).some(cb => cb.checked);
      if (isAnyChecked) {
        invalidBlock.classList.remove('is-invalid');
        const errorMsg = invalidBlock.querySelector('.invalid-feedback');
        if (errorMsg) errorMsg.style.display = 'none';
      } else {
        invalidBlock.classList.add('is-invalid');
        const errorMsg = invalidBlock.querySelector('.invalid-feedback');
        if (errorMsg) errorMsg.style.display = 'block';
      }
    }
  });
}

/* =====================================================================
   7) POPOVER ПРЕДПРОСМОТР ОБЗОРА
   (review_multiple_form)
   ===================================================================== */
function initReviewPreviewPopover({ previewItemSelector, fetchUrlTemplate }) {
  const previewItems = document.querySelectorAll(previewItemSelector);
  if (!previewItems.length) return;

  let activePopover = null;
  let activeItem = null;
  const showTimers = new Map();
  const hideTimers = new Map();
  const htmlCache = new Map(); // чтобы не запрашивать один и тот же контент повторно

  previewItems.forEach(item => {
    item.addEventListener('mouseenter', () => {
      const timerId = setTimeout(() => showPopover(item), 700); // ← можно 1500
      showTimers.set(item, timerId);
    });

    item.addEventListener('mouseleave', () => {
      if (showTimers.has(item)) {
        clearTimeout(showTimers.get(item));
        showTimers.delete(item);
      }
      hideIfNeeded(item);
    });
  });

  async function showPopover(item) {
    showTimers.delete(item);
    if (!item.matches(':hover')) return;

    if (activePopover && activeItem !== item) {
      activePopover.hide();
      activePopover = null;
      activeItem = null;
    }

    const checkbox = item.querySelector('input[type="checkbox"]');
    if (!checkbox) return;
    const pk = checkbox.value;
    if (!pk) return;

    let snippet = htmlCache.get(pk);
    if (!snippet) {
      try {
        const url = fetchUrlTemplate.replace('{id}', pk);
        const resp = await fetch(url);
        if (!resp.ok) throw new Error(`Response not OK, status=${resp.status}`);
        const data = await resp.json();
        snippet = data.html;
        htmlCache.set(pk, snippet);
      } catch (err) {
        console.error('Ошибка загрузки preview:', err);
        return;
      }
    }

    const pop = new bootstrap.Popover(item, {
      content: snippet,
      html: true,
      placement: 'right',
      trigger: 'manual',
      popperConfig: {
        modifiers: [
          {
            name: 'flip',
            options: { fallbackPlacements: [] }
          },
          {
            name: 'offset',
            options: {
              offset: [8, 30] // ← отступ справа
            }
          },
          {
            name: 'preventOverflow',
            options: { padding: 8 }
          }
        ]
      }
    });
    pop.show();
    activePopover = pop;
    activeItem = item;

    item.addEventListener('shown.bs.popover', () => {
      const popoverEl = document.querySelector('.popover');
      if (!popoverEl) return;

      popoverEl.addEventListener('mouseleave', () => {
        // задержка перед скрытием
        setTimeout(() => {
          const stillHovered = item.matches(':hover') || popoverEl.matches(':hover');
          if (!stillHovered && activePopover) {
            activePopover.hide();
            activePopover = null;
            activeItem = null;
          }
        }, 500);
      });
    });
  }

  function hideIfNeeded(item) {
    if (activeItem === item && activePopover) {
      const popoverEl = document.querySelector('.popover');
      if (popoverEl && popoverEl.matches(':hover')) return;

      // задержка перед скрытием
      setTimeout(() => {
        const stillHovered = item.matches(':hover') || (popoverEl && popoverEl.matches(':hover'));
        if (!stillHovered && activePopover) {
          activePopover.hide();
          activePopover = null;
          activeItem = null;
        }
      }, 500);
    }
  }
}

/* =====================================================================
   8) «СТРЕЛОЧКИ» ВВЕРХ/ВНИЗ В <SELECT>
   (review_form, review_mail)
   ===================================================================== */
function initSelectArrows(selectors) {
  selectors.forEach(sel => {
    const selectEl = document.querySelector(sel);
    if (!selectEl) return;

    selectEl.addEventListener('focus', function(e) {
      e.target.classList.add('arrow-up');
    });
    selectEl.addEventListener('blur', function(e) {
      e.target.classList.remove('arrow-up');
    });
  });
}

/* =====================================================================
   9) АВТОМАТИЧЕСКОЕ РАСШИРЕНИЕ TEXTAREA
   (review_form)
   ===================================================================== */
function autoExpandTextarea(selector) {
  const textarea = document.querySelector(selector);
  if (!textarea) return;

  function autoExpand(el) {
    el.style.height = 'auto';
    const baseHeightPx = 40; // минимальная высота
    const newHeight = Math.max(el.scrollHeight, baseHeightPx);
    el.style.height = newHeight + 'px';
  }

  // Срабатывает при вводе
  textarea.addEventListener('input', function() {
    autoExpand(this);
  });

  // Срабатывает один раз при загрузке
  autoExpand(textarea);
}

/* =====================================================================
   10) ЛОГИКА "СТАТУС -> ПОКАЗЫВАЕМ/СКРЫВАЕМ ДАТУ СТАТУСА"
   (review_form)
   ===================================================================== */
function initStatusDateVisibility({ statusSelector, dateGroupSelector, dateInputSelector }) {
  const statusSelect = document.querySelector(statusSelector);
  const dateGroup = document.querySelector(dateGroupSelector);
  const dateInput = document.querySelector(dateInputSelector);

  if (!statusSelect || !dateGroup || !dateInput) return;

  function updatePowerDateVisibility() {
    if (!statusSelect.value) {
      // Если ничего не выбрано, скрываем поле
      dateGroup.style.display = 'none';
      dateInput.removeAttribute('required');
    } else {
      // Если есть значение в статусе, показываем
      dateGroup.style.display = '';
      dateInput.setAttribute('required', 'true');
    }
  }

  // При изменении статуса
  statusSelect.addEventListener('change', updatePowerDateVisibility);
  // Сразу при загрузке
  updatePowerDateVisibility();
}

/* =====================================================================
   11) ТЕМНАЯ ТЕМА — ПЕРЕКЛЮЧАТЕЛЬ + ИКОНКА
   (работает на всех страницах кроме main-page)
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
   12) КАСТОМНЫЙ DROPDOWN (если используется в других фильтрах)
   ===================================================================== */
function initCustomDropdowns() {
  const dropdowns = document.querySelectorAll(".custom-dropdown");
  dropdowns.forEach(dropdown => {
    const toggleBtn = dropdown.querySelector(".dropdown-toggle-btn");
    const options = dropdown.querySelector(".dropdown-options");
    const hiddenInput = dropdown.querySelector("input[type='hidden']");
    const selectedText = dropdown.querySelector(".selected-text");

    toggleBtn.addEventListener("click", () => {
      dropdown.classList.toggle("open");
    });

    options.querySelectorAll("li").forEach(option => {
      option.addEventListener('click', () => {
        const value = option.dataset.value;
        const text = option.innerText;
        hiddenInput.value = value;
        selectedText.textContent = text;
        dropdown.classList.remove("open");
        applyFilters(); // запускаем фильтрацию
      });
    });

    document.addEventListener("click", (e) => {
      if (!dropdown.contains(e.target)) {
        dropdown.classList.remove("open");
      }
    });
  });
}

/* =====================================================================
   13) ФИЛЬТРАЦИЯ НОВОСТЕЙ / РИСКОВ + toggle-категории
   ===================================================================== */
function initNewsFilters() {
  const newsItems = document.querySelectorAll('.news-item, .card[data-direct], .preview-item');
  const categoryRadios = document.querySelectorAll('input[name="category"].category-toggle');
  const rubricCheckboxes = document.querySelectorAll('input[name="rubrics"]');
  const subjectRadios = document.querySelectorAll('input[name="subject"]');
  const kindRadios = document.querySelectorAll('input[name="kind"]');
  const directRadios = document.querySelectorAll('input[name="direct"]');
  const dateFromInput = document.getElementById('date-from');
  const dateToInput = document.getElementById('date-to');
  const resetButton = document.getElementById('reset-filters');

  if (!newsItems.length) return;

  // Инициализация флага выбора
  categoryRadios.forEach(r => r.dataset.wasChecked = 'false');

  // Автоматическое обновление данных прогрессивной загрузки при загрузке страницы
  if (window.refreshProgressiveLoading) {
    // Небольшая задержка чтобы страница полностью загрузилась
    setTimeout(() => {
      window.refreshProgressiveLoading();
    }, 1000);
  }

  async function filterItems() {
    const selectedCategory = document.querySelector('input[name="category"]:checked')?.value?.trim();
    const selectedRubrics = Array.from(rubricCheckboxes)
      .filter(cb => cb.checked)
      .map(cb => cb.value.trim());
    const selectedDirect = document.querySelector('input[name="direct"]:checked')?.value?.trim();
    const selectedSubject = document.querySelector('input[name="subject"]:checked')?.value?.trim();
    const selectedKind = document.querySelector('input[name="kind"]:checked')?.value?.trim();
    const dateFrom = dateFromInput?.value ? new Date(dateFromInput.value) : null;
    const dateTo = dateToInput?.value ? new Date(dateToInput.value) : null;

    // Получаем актуальный список элементов (может обновиться после дозагрузки)
    const currentNewsItems = document.querySelectorAll('.news-item, .card[data-direct], .preview-item');

    currentNewsItems.forEach(item => {
      const itemCategory = item.dataset.category?.trim();
      let itemRubrics = [];
      try {
        const rawRubrics = item.dataset.rubrics;
        itemRubrics = JSON.parse(rawRubrics || '[]');
      } catch (e) {
        itemRubrics = [];
      }
      const itemDirect = item.dataset.direct?.trim();
      const itemSubject = item.dataset.subject?.trim();
      const itemKind = item.dataset.kind?.trim();
      const itemDate = item.dataset.publishDate ? new Date(item.dataset.publishDate) : null;

      const categoryMatch = !selectedCategory || itemCategory?.trim().toLowerCase() === selectedCategory.trim().toLowerCase();
      const rubricsMatch = selectedRubrics.length === 0 || selectedRubrics.some(r => itemRubrics.includes(r));
      const directMatch = !selectedDirect || itemDirect === selectedDirect;
      const subjectMatch = !selectedSubject || itemSubject === selectedSubject;
      const kindMatch = !selectedKind || itemKind === selectedKind;

      let dateMatch = true;
      if (itemDate) {
        if (dateFrom && itemDate < dateFrom) dateMatch = false;
        if (dateTo && itemDate > dateTo) dateMatch = false;
      }

      item.style.display =
        categoryMatch &&
        rubricsMatch &&
        directMatch &&
        subjectMatch &&
        kindMatch &&
        dateMatch
          ? 'block'
          : 'none';
    });
  }

  // Публичная функция для применения фильтров (используется при дозагрузке)
  window.applyCurrentFilters = filterItems;

  // === Toggle-поведение для категорий ===
  categoryRadios.forEach(radio => {
    radio.addEventListener('click', function () {
      if (this.dataset.wasChecked === 'true') {
        // Повторный клик — снимаем все
        categoryRadios.forEach(r => {
          r.checked = false;
          r.dataset.wasChecked = 'false';
        });
        filterItems();
      } else {
        // Устанавливаем только этот, сбрасываем остальные
        categoryRadios.forEach(r => r.dataset.wasChecked = 'false');
        this.dataset.wasChecked = 'true';
        filterItems();
      }
    });
  });

  rubricCheckboxes.forEach(cb => cb?.addEventListener('change', filterItems));
  [...subjectRadios, ...kindRadios, ...directRadios].forEach(r => r?.addEventListener('change', filterItems));
  dateFromInput?.addEventListener('change', filterItems);
  dateToInput?.addEventListener('change', filterItems);
  
  resetButton?.addEventListener('click', function () {
    [...categoryRadios, ...subjectRadios, ...kindRadios, ...directRadios].forEach(r => {
      r.checked = false;
      r.dataset.wasChecked = 'false';
    });
    rubricCheckboxes.forEach(cb => (cb.checked = false));
    if (dateFromInput) dateFromInput.value = '';
    if (dateToInput) dateToInput.value = '';
    filterItems();
  });

  filterItems(); // запуск при загрузке
}


function initProgressiveLoading() {
  // Проверяем, что мы на странице reviews и есть данные
  if (!window.reviewsData || !document.getElementById('news-container')) {
    return;
  }

  const newsContainer = document.getElementById('news-container');
  const loadingIndicator = document.getElementById('loading-indicator');
  
  let isLoading = false;
  let isFullyLoaded = false;
  let allNewsItems = [];
  
  // Собираем начальные элементы
  function collectInitialItems() {
    const initialItems = Array.from(document.querySelectorAll('.news-item'));
    allNewsItems = initialItems.map(item => ({
      element: item,
      category: item.dataset.category?.trim(),
      rubrics: JSON.parse(item.dataset.rubrics || '[]'),
      publishDate: item.dataset.publishDate,
      html: item.outerHTML
    }));
  }

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
  async function loadMoreReviews() {
    if (isLoading || isFullyLoaded) return;
    
    isLoading = true;
    showLoadingIndicator();

    try {
      const offset = window.reviewsData.loadedCount;
      const response = await fetch(`/reviews/api/load-more/?offset=${offset}&limit=50`);
      
      if (!response.ok) {
        throw new Error('API endpoint не найден');
      }

      const data = await response.json();
      
      // Добавляем новые элементы в DOM
      data.reviews.forEach(review => {
        const reviewElement = createReviewElement(review);
        newsContainer.appendChild(reviewElement);
        
        // Добавляем в наш массив для поиска
        allNewsItems.push({
          element: reviewElement,
          category: review.category,
          rubrics: review.rubrics,
          publishDate: review.publish_date,
          html: reviewElement.outerHTML
        });
      });

      // Обновляем счетчики
      window.reviewsData.loadedCount += data.reviews.length;
      window.reviewsData.hasMore = data.has_more;
      
      if (!data.has_more) {
        isFullyLoaded = true;
      }

      // Применяем текущие фильтры к новым элементам
      if (window.applyCurrentFilters) {
        window.applyCurrentFilters();
      }

    } catch (error) {
      console.warn('API endpoint для прогрессивной загрузки еще не создан:', error);
      // Fallback: считаем что все данные уже загружены
      isFullyLoaded = true;
      window.reviewsData.hasMore = false;
    } finally {
      isLoading = false;
      hideLoadingIndicator();
    }
  }

  // Создание HTML элемента обзора
  function createReviewElement(review) {
    const div = document.createElement('div');
    div.className = 'card mb-3 shadow-sm position-relative news-item';
    div.dataset.category = review.category;
    div.dataset.rubrics = JSON.stringify(review.rubrics);
    div.dataset.publishDate = review.publish_date;
    
    const badgeColor = review.category === 'Принятые изменения' ? '#28a745' :
                      review.category === 'Проекты НПА' ? '#ffa500' : '#6c757d';
    
    div.innerHTML = `
      <div class="card-body">
        <div class="status-line mb-2">
          <small class="text-muted">
            <span class="rubric">
              ${review.rubrics.map(r => `<span class="badge rounded-pill bg-secondary">${r}</span>`).join('')}
            </span>
            <span style="margin-right: 0.1rem; margin-left: 0.1rem"></span>
            <span class="created-date">| ${review.formatted_date}</span>
            <span class="ms-2 badge rounded-pill" style="background-color: ${badgeColor};">
              ${review.category}
            </span>
          </small>
        </div>
        <h5 class="card-title fw-bold">${review.title}</h5>
        <p class="card-text">${review.description}</p>
        ${review.power_date ? `<p class="text-muted small mb-1"><strong>Статус:</strong> ${review.powers} ${review.power_date}</p>` : ''}
        <a href="${review.url}" class="stretched-link"></a>
      </div>
    `;
    
    return div;
  }

  // Запуск фоновой загрузки
  function startBackgroundLoading() {
    // Небольшая задержка, чтобы страница успела отрендериться
    setTimeout(() => {
      if (window.reviewsData.hasMore) {
        loadMoreReviews();
      } else {
        // ДЕМО: Если нет данных о том что есть еще записи, 
        // имитируем что они есть для демонстрации
        console.log('🚀 Прогрессивная загрузка инициализирована');
        console.log('📊 Загружено записей:', window.reviewsData.loadedCount);
        console.log('📈 Всего записей:', window.reviewsData.totalCount);
      }
    }, 500);
  }

  // Публичная функция для проверки состояния загрузки
  window.isReviewsFullyLoaded = function() {
    return isFullyLoaded;
  };

  // Публичная функция для принудительной загрузки (если пользователь ищет)
  window.ensureFullyLoaded = function() {
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

  // Публичная функция для обновления данных после добавления новых записей
  window.refreshProgressiveLoading = async function() {
    try {
      // Получаем актуальную информацию о количестве записей
      const response = await fetch('/reviews/api/total-count/');
      if (response.ok) {
        const data = await response.json();
        
        // Обновляем метаданные
        window.reviewsData.totalCount = data.total_count;
        
        // Если новых записей больше чем было загружено, активируем загрузку
        if (data.total_count > window.reviewsData.loadedCount) {
          window.reviewsData.hasMore = true;
          isFullyLoaded = false;
          
          console.log('🔄 Обнаружены новые записи! Активирую прогрессивную загрузку...');
          console.log('📊 Всего записей:', data.total_count);
          console.log('📊 Загружено:', window.reviewsData.loadedCount);
          
          // Запускаем загрузку новых данных
          await loadMoreReviews();
        }
      }
    } catch (error) {
      console.warn('Не удалось обновить данные прогрессивной загрузки:', error);
    }
  };

  // Инициализация
  collectInitialItems();
  startBackgroundLoading();
}