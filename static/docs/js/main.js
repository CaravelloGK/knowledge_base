/* <editor-fold desc="===== Список и фильтрация =====" */
/**
 * ФИЛЬТРАЦИЯ СПИСКА ДОКУМЕНТОВ
 * Обрабатывает фильтрацию карточек документов на главной странице списка
 * Фильтрует по направлению бизнеса (direct) и типу документа (subject)
 */
document.addEventListener('DOMContentLoaded', function() {
    // Сохраняем все карточки при первой загрузке
    const row = document.querySelector('.docs-page .row.g-3');
    if (!row) return;
    const allCards = Array.from(row.querySelectorAll('.col-md-6'));
    // Сохраняем копии DOM-элементов (чтобы не терять их при пересборке)
    const allCardsClones = allCards.map(card => card.cloneNode(true));

    /**
     * Фильтрует карточки документов на основе выбранных радиокнопок
     * Использует клонированные DOM-элементы для сохранения исходного состояния
     */
    function filterCards() {
        const selectedDirect = document.querySelector('input[name="direct"]:checked')?.value;
        const selectedSubject = document.querySelector('input[name="subject"]:checked')?.value;

        // Фильтруем по сохранённым копиям
        const filtered = allCardsClones.filter(card => {
            const item = card.querySelector('.news-item');
            const itemDirect = item?.dataset.direct;
            const itemSubject = item?.dataset.subject;
            const directMatch = !selectedDirect || itemDirect === selectedDirect;
            const subjectMatch = !selectedSubject || itemSubject === selectedSubject;
            return directMatch && subjectMatch;
        });

        // Очищаем .row и добавляем только подходящие карточки
        row.innerHTML = '';
        if (filtered.length) {
            filtered.forEach(card => row.appendChild(card.cloneNode(true)));
        } else {
            row.innerHTML = '<p class="text-muted">Нет документов.</p>';
        }
    }

    // Навешиваем обработчики на фильтры
    document.querySelectorAll('input[name="direct"], input[name="subject"]').forEach(input => {
        input.addEventListener('change', filterCards);
    });

    // Кнопка сброса фильтров
    const resetButton = document.getElementById('reset-filters');
    if (resetButton) {
        resetButton.addEventListener('click', function() {
            setTimeout(filterCards, 10); // Даем фильтрам сброситься
        });
    }

    // Первичная фильтрация
    filterCards();
});
/* </editor-fold> */

/* <editor-fold desc="===== Формы и динамические списки =====" */
/**
 * ДИНАМИЧЕСКОЕ ЗАПОЛНЕНИЕ КАТЕГОРИЙ
 * Заполняет выпадающий список категорий на основе выбранного глобального раздела
 * Работает как на формах создания, так и на формах редактирования
 */
document.addEventListener('DOMContentLoaded', function() {
  const globalSectionSelect = document.getElementById('id_global_section');
  const categorySelect = document.getElementById('id_category');
  
  if (globalSectionSelect && categorySelect) {
    globalSectionSelect.addEventListener('change', function() {
      const globalSectionId = this.value;
      categorySelect.innerHTML = '<option value="">Загрузка...</option>';
      
      // Проверяем, находимся ли мы на форме редактирования (по паттерну URL)
      const isUpdateForm = window.location.pathname.includes('/update/');
      const fetchUrl = isUpdateForm 
        ? `/docs/ajax/get-categories/?global_section_id=${globalSectionId}`  // URL формы редактирования
        : `/docs/ajax/get-categories/?global_section_id=${globalSectionId}`; // URL формы создания
      
      fetch(fetchUrl)
        .then(response => response.json())
        .then(data => {
          categorySelect.innerHTML = '<option value="">Выбери рубрику</option>';
          data.categories.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat.id;
            option.textContent = cat.name;
            categorySelect.appendChild(option);
          });
        })
        .catch(error => {
          console.error('Error fetching categories:', error);
          categorySelect.innerHTML = '<option value="">Ошибка загрузки</option>';
        });
    });
  }

  /**
   * КОНТРОЛЛЕР ВИДИМОСТИ ПОЛЯ SECTION
   * Показывает/скрывает поле раздела на основе выбора глобального раздела
   * Показывается только для "Корпоративный бизнес"
   */
  const sectionGroup = document.getElementById('group-section');
  if (globalSectionSelect && sectionGroup) {
    function updateSectionVisibility() {
      const selectedOption = globalSectionSelect.options[globalSectionSelect.selectedIndex];
      if (selectedOption && selectedOption.text.trim() === 'Корпоративный бизнес') {
        sectionGroup.style.display = '';
      } else {
        sectionGroup.style.display = 'none';
      }
    }
    // Запускаем при загрузке страницы и при изменении
    updateSectionVisibility();
    globalSectionSelect.addEventListener('change', updateSectionVisibility);
  }
});
/* </editor-fold> */

/* <editor-fold desc="===== Загрузка файлов и Drag-Drop =====" */
/**
 * УНИВЕРСАЛЬНАЯ ФУНКЦИОНАЛЬНОСТЬ ЗОНЫ ПЕРЕТАСКИВАНИЯ
 * Обрабатывает drag-and-drop файлов и загрузку по клику
 * Работает как на формах создания, так и на формах обновления
 */
document.addEventListener('DOMContentLoaded', () => {
  const dropArea = document.getElementById('dropArea');
  if (!dropArea) return;
  
  const preventDefaults = e => { e.preventDefault(); e.stopPropagation(); };
  const defaultContent = dropArea.innerHTML; // сохраняем изначальную разметку
  const formEl = dropArea.closest('form');
  
  // Предотвращаем поведение drag по умолчанию
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(ev => {
    dropArea.addEventListener(ev, preventDefaults, false);
  });
  
  // Подсвечиваем зону при перетаскивании над ней
  ['dragenter', 'dragover'].forEach(ev => {
    dropArea.addEventListener(ev, () => dropArea.classList.add('dragover'), false);
  });
  
  // Убираем подсветку при уходе курсора или сбросе файлов
  ['dragleave', 'drop'].forEach(ev => {
    dropArea.addEventListener(ev, () => dropArea.classList.remove('dragover'), false);
  });
  
  /**
   * Открывает системный диалог выбора файлов, создавая временный input элемент
   */
  function openFileDialog() {
    const tmpInput = document.createElement('input');
    tmpInput.type = 'file';
    tmpInput.multiple = true;
    tmpInput.style.display = 'none';
    tmpInput.addEventListener('change', () => {
      if (tmpInput.files.length) {
        handleFiles(tmpInput.files);
      }
      tmpInput.remove();
    });
    formEl.appendChild(tmpInput);
    tmpInput.click();
  }

  dropArea.addEventListener('click', openFileDialog);
  dropArea.addEventListener('drop', e => {
    handleFiles(e.dataTransfer.files);
  });

  /**
   * Обрабатывает выбранные/перетащенные файлы
   * @param {FileList} fileList - Файлы для обработки
   */
  function handleFiles(fileList) {
    Array.from(fileList).forEach(f => addFile(f));
    renderList();
  }

  const fileStore = []; // [{file, inputEl}] - Хранилище для файлов и их input элементов

  /**
   * Добавляет файл в хранилище и создает скрытый input для отправки формы
   * @param {File} file - Файл для добавления
   */
  function addFile(file) {
    const hiddenInput = document.createElement('input');
    hiddenInput.type = 'file';
    hiddenInput.name = 'attachments';
    hiddenInput.style.display = 'none';
    const dtLocal = new DataTransfer();
    dtLocal.items.add(file);
    hiddenInput.files = dtLocal.files;
    formEl.appendChild(hiddenInput);
    fileStore.push({ file: file, input: hiddenInput });
  }

  /**
   * Отрисовывает список файлов в зоне перетаскивания
   * Показывает превью файлов с кнопками удаления
   */
  function renderList() {
    if (fileStore.length === 0) {
      dropArea.innerHTML = defaultContent;
      dropArea.style.justifyContent = 'center';
      dropArea.style.alignItems = 'center';
      return;
    }

    // Создаем превью
    const preview = document.createElement('div');
    preview.style.display = 'flex';
    preview.style.flexDirection = 'column';
    preview.style.gap = '6px';

    fileStore.forEach((obj, idx) => {
      const f = obj.file;
      const row = document.createElement('div');
      row.style.display = 'flex';
      row.style.alignItems = 'center';
      row.style.gap = '6px';
      
      // Номер файла
      const num = document.createElement('span');
      num.textContent = (idx + 1) + '.';
      
      // Иконка + имя файла
      const info = document.createElement('span');
      info.innerHTML = `<img src="/static/img/file.svg" style="width:18px;height:18px;"> ${f.name}`;
      
      // Кнопка удаления
      const del = document.createElement('button');
      del.type = 'button';
      del.textContent = '✕';
      del.style.border = 'none';
      del.style.background = 'transparent';
      del.style.cursor = 'pointer';
      del.addEventListener('click', e => {
        e.stopPropagation();
        // удаляем скрытый input
        obj.input.remove();
        fileStore.splice(idx, 1);
        renderList();
      });

      row.appendChild(num);
      row.appendChild(info);
      row.appendChild(del);
      preview.appendChild(row);
    });
    
    // Обновляем отображение зоны перетаскивания
    dropArea.innerHTML = '';
    dropArea.style.justifyContent = 'flex-start';
    dropArea.style.alignItems = 'flex-start';
    dropArea.appendChild(preview);
  }
});
/* </editor-fold> */

/* <editor-fold desc="===== Детали документа =====" */
/**
 * ПОИСК В ОГЛАВЛЕНИИ
 * Включает функциональность живого поиска в боковой панели оглавления документа
 * Фильтрует элементы оглавления на основе пользовательского ввода
 */
$(document).ready(function() {
   $('#tocSearch').on('input', function() {
       const searchText = $(this).val().toLowerCase();

       $('.toc-item').each(function() {
           const item = $(this);
           const text = item.text().toLowerCase();

           if (text.includes(searchText)) {
               item.show();
           } else {
               item.hide();
           }
       });
   });
});

/**
 * СЧЕТЧИК СЛАЙДОВ ПРЕЗЕНТАЦИИ
 * Обновляет счетчик слайдов для карусели презентации
 * Показывает текущий номер слайда из общего количества слайдов
 */
document.addEventListener('DOMContentLoaded', function() {
  const carousel = document.getElementById('pptxCarousel');
  if (carousel) {
    const counter = document.getElementById('slide-counter');
    const total = JSON.parse(document.getElementById('slides_total').textContent);
    
    carousel.addEventListener('slid.bs.carousel', function(event) {
      const idx = event.to + 1;
      counter.textContent = `Слайд ${idx} из ${total}`;
    });
  }
});
/* </editor-fold> */