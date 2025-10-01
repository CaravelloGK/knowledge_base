/* =====================================================================
   ФИЛЬТРАЦИЯ ЮРИДИЧЕСКИХ ЛИЦ
   ===================================================================== */

/**
 * Инициализация фильтров для страницы списка юридических лиц
 * Фильтрует карточки по названию, ИНН, ОГРН, дате создания и дате обновления
 */
document.addEventListener('DOMContentLoaded', function() {
    // Получаем все элементы фильтров
    const nameFilter = document.getElementById('name-filter');
    const innFilter = document.getElementById('inn-filter');
    const ogrnFilter = document.getElementById('ogrn-filter');
    const createdDateFromInput = document.getElementById('created-date-from');
    const createdDateToInput = document.getElementById('created-date-to');
    const updatedDateFromInput = document.getElementById('updated-date-from');
    const updatedDateToInput = document.getElementById('updated-date-to');
    const resetButton = document.getElementById('reset-filters');

    // Проверяем, что мы на странице со списком юридических лиц
    const entitiesContainer = document.getElementById('entities-container');
    if (!entitiesContainer) {
        console.log('entities-container не найден');
        return;
    }

    // Отладочная информация
    console.log('Фильтры инициализированы:', {
        nameFilter: !!nameFilter,
        innFilter: !!innFilter,
        ogrnFilter: !!ogrnFilter,
        createdDateFromInput: !!createdDateFromInput,
        createdDateToInput: !!createdDateToInput,
        updatedDateFromInput: !!updatedDateFromInput,
        updatedDateToInput: !!updatedDateToInput,
        resetButton: !!resetButton,
        entitiesContainer: !!entitiesContainer
    });

    /**
     * Функция для подсветки найденного текста
     */
    function highlightText(element, query, className = 'highlight') {
        if (!query || query.length < 2) {
            // Убираем подсветку если запрос пустой или слишком короткий
            removeHighlight(element);
            return;
        }

        const walker = document.createTreeWalker(
            element,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );

        const textNodes = [];
        let node;
        while (node = walker.nextNode()) {
            textNodes.push(node);
        }

        textNodes.forEach(textNode => {
            const text = textNode.textContent;
            const regex = new RegExp(`(${query})`, 'gi');

            if (regex.test(text)) {
                const highlightedText = text.replace(regex, `<mark class="${className}">$1</mark>`);
                const wrapper = document.createElement('span');
                wrapper.innerHTML = highlightedText;
                textNode.parentNode.replaceChild(wrapper, textNode);
            }
        });
    }

    /**
     * Функция для удаления подсветки
     */
    function removeHighlight(element) {
        const highlights = element.querySelectorAll('mark.highlight');
        highlights.forEach(mark => {
            const parent = mark.parentNode;
            parent.replaceChild(document.createTextNode(mark.textContent), mark);
            parent.normalize();
        });
    }

    /**
     * Основная функция фильтрации
     * Проходит по всем карточкам и показывает/скрывает их на основе фильтров
     */
    function filterEntities() {
        const nameQuery = nameFilter ? nameFilter.value.toLowerCase().trim() : '';
        const innQuery = innFilter ? innFilter.value.toLowerCase().trim() : '';
        const ogrnQuery = ogrnFilter ? ogrnFilter.value.toLowerCase().trim() : '';
        const createdDateFrom = createdDateFromInput ? createdDateFromInput.value : '';
        const createdDateTo = createdDateToInput ? createdDateToInput.value : '';
        const updatedDateFrom = updatedDateFromInput ? updatedDateFromInput.value : '';
        const updatedDateTo = updatedDateToInput ? updatedDateToInput.value : '';

        console.log('Фильтрация запущена:', {
            nameQuery, innQuery, ogrnQuery,
            createdDateFrom, createdDateTo,
            updatedDateFrom, updatedDateTo
        });

        // Преобразуем даты для сравнения
        const createdDateFromObj = createdDateFrom ? new Date(createdDateFrom) : null;
        const createdDateToObj = createdDateTo ? new Date(createdDateTo) : null;
        const updatedDateFromObj = updatedDateFrom ? new Date(updatedDateFrom) : null;
        const updatedDateToObj = updatedDateTo ? new Date(updatedDateTo) : null;

        // Получаем все карточки юридических лиц
        const entityCards = entitiesContainer.querySelectorAll('.entity-card');

        let visibleCount = 0;

        entityCards.forEach(card => {
            const entityName = card.dataset.entityName || '';
            const entityInn = card.dataset.entityInn || '';
            const entityOgrn = card.dataset.entityOgrn || '';
            const entityCreatedDateStr = card.dataset.createdDate || '';
            const entityUpdatedDateStr = card.dataset.updatedDate || '';

            // Проверка по названию
            const nameMatch = !nameQuery || entityName.includes(nameQuery);

            // Проверка по ИНН
            const innMatch = !innQuery || entityInn.toLowerCase().includes(innQuery);

            // Проверка по ОГРН
            const ogrnMatch = !ogrnQuery || entityOgrn.toLowerCase().includes(ogrnQuery);

            // Проверка по дате создания
            let createdDateMatch = true;
            if (entityCreatedDateStr && (createdDateFromObj || createdDateToObj)) {
                const entityCreatedDate = new Date(entityCreatedDateStr);
                if (createdDateFromObj && entityCreatedDate < createdDateFromObj) {
                    createdDateMatch = false;
                }
                if (createdDateToObj && entityCreatedDate > createdDateToObj) {
                    createdDateMatch = false;
                }
            }

            // Проверка по дате обновления
            let updatedDateMatch = true;
            if (entityUpdatedDateStr && (updatedDateFromObj || updatedDateToObj)) {
                const entityUpdatedDate = new Date(entityUpdatedDateStr);
                if (updatedDateFromObj && entityUpdatedDate < updatedDateFromObj) {
                    updatedDateMatch = false;
                }
                if (updatedDateToObj && entityUpdatedDate > updatedDateToObj) {
                    updatedDateMatch = false;
                }
            }

            // Показываем или скрываем карточку
            const shouldShow = nameMatch && innMatch && ogrnMatch && createdDateMatch && updatedDateMatch;
            card.style.display = shouldShow ? 'block' : 'none';

            if (shouldShow) {
                visibleCount++;

                // Убираем предыдущую подсветку
                removeHighlight(card);

                // Добавляем подсветку для текстовых запросов
                if (nameQuery && nameQuery.length >= 2) {
                    const nameElement = card.querySelector('.entity-name');
                    if (nameElement) {
                        highlightText(nameElement, nameQuery);
                    }
                }

                if (innQuery && innQuery.length >= 2) {
                    const innElement = card.querySelector('.entity-inn');
                    if (innElement) {
                        highlightText(innElement, innQuery);
                    }
                }

                if (ogrnQuery && ogrnQuery.length >= 2) {
                    const ogrnElement = card.querySelector('.entity-ogrn');
                    if (ogrnElement) {
                        highlightText(ogrnElement, ogrnQuery);
                    }
                }
            } else {
                // Убираем подсветку для скрытых карточек
                removeHighlight(card);
            }
        });

        // Показываем сообщение если нет результатов
        updateEmptyState(visibleCount);
    }

    /**
     * Показывает/скрывает сообщение об отсутствии результатов
     */
    function updateEmptyState(visibleCount) {
        let emptyMessage = entitiesContainer.querySelector('.empty-state-message');

        if (visibleCount === 0) {
            if (!emptyMessage) {
                emptyMessage = document.createElement('div');
                emptyMessage.className = 'empty-state-message text-center py-5';
                emptyMessage.innerHTML = `
                    <div class="text-muted">
                        <i class="bi bi-search" style="font-size: 3rem; opacity: 0.3;"></i>
                        <h5 class="mt-3">Юридические лица не найдены</h5>
                        <p>Попробуйте изменить параметры поиска</p>
                    </div>
                `;
                entitiesContainer.appendChild(emptyMessage);
            }
            emptyMessage.style.display = 'block';
        } else if (emptyMessage) {
            emptyMessage.style.display = 'none';
        }
    }

    /**
     * Сброс всех фильтров к значениям по умолчанию
     */
    function resetFilters() {
        // Сбрасываем текстовые поля
        if (nameFilter) nameFilter.value = '';
        if (innFilter) innFilter.value = '';
        if (ogrnFilter) ogrnFilter.value = '';

        // Принудительная очистка полей дат
        const dateFields = [
            'created-date-from', 'created-date-to',
            'updated-date-from', 'updated-date-to'
        ];

        dateFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.value = '';
                field.removeAttribute('value');
                // Принудительное обновление DOM
                field.dispatchEvent(new Event('input', { bubbles: true }));
                field.dispatchEvent(new Event('change', { bubbles: true }));
            }
        });

        console.log('Фильтры сброшены');

        // Убираем всю подсветку
        const entityCards = entitiesContainer.querySelectorAll('.entity-card');
        entityCards.forEach(card => {
            removeHighlight(card);
        });

        // Применяем фильтры
        setTimeout(filterEntities, 10);
    }

    // Навешиваем обработчики событий
    if (nameFilter) {
        nameFilter.addEventListener('input', filterEntities);
    }

    if (innFilter) {
        innFilter.addEventListener('input', filterEntities);
    }

    if (ogrnFilter) {
        ogrnFilter.addEventListener('input', filterEntities);
    }

    if (createdDateFromInput) {
        createdDateFromInput.addEventListener('change', filterEntities);
    }

    if (createdDateToInput) {
        createdDateToInput.addEventListener('change', filterEntities);
    }

    if (updatedDateFromInput) {
        updatedDateFromInput.addEventListener('change', filterEntities);
    }

    if (updatedDateToInput) {
        updatedDateToInput.addEventListener('change', filterEntities);
    }

    if (resetButton) {
        resetButton.addEventListener('click', resetFilters);
    }

    // Первичная фильтрация при загрузке страницы
    filterEntities();
});