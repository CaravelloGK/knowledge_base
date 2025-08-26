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

/* =====================================================================
   ФИЛЬТРАЦИЯ СДЕЛОК
   ===================================================================== */

/**
 * Инициализация фильтров для страницы списка сделок
 * Фильтрует карточки по названию, ИНН, ОГРН, должнику, дате создания и дате обновления
 */
document.addEventListener('DOMContentLoaded', function() {
    // Получаем все элементы фильтров для сделок
    const dealNumberFilter = document.getElementById('deal-number-filter');
    const dealCreditProductFilter = document.getElementById('deal-credit-product-filter');
    const dealBorrowerFilter = document.getElementById('deal-borrower-filter');
    const dealCreatedDateFromInput = document.getElementById('deal-created-date-from');
    const dealCreatedDateToInput = document.getElementById('deal-created-date-to');
    const resetDealButton = document.getElementById('reset-deal-filters');

    // Проверяем, что мы на странице со списком сделок
    const dealsContainer = document.getElementById('deals-container');
    if (!dealsContainer) {
        console.log('deals-container не найден');
    return;
  }

    // Отладочная информация
    console.log('Фильтры сделок инициализированы:', {
        dealNumberFilter: !!dealNumberFilter,
        dealCreditProductFilter: !!dealCreditProductFilter,
        dealBorrowerFilter: !!dealBorrowerFilter,
        dealCreatedDateFromInput: !!dealCreatedDateFromInput,
        dealCreatedDateToInput: !!dealCreatedDateToInput,
        resetDealButton: !!resetDealButton,
        dealsContainer: !!dealsContainer
    });

    /**
     * Функция для подсветки найденного текста в сделках
     */
    function highlightDealText(element, query, className = 'highlight') {
        if (!query || query.length < 2) {
            removeDealHighlight(element);
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
     * Функция для удаления подсветки в сделках
     */
    function removeDealHighlight(element) {
        const highlights = element.querySelectorAll('mark.highlight');
        highlights.forEach(mark => {
            const parent = mark.parentNode;
            parent.replaceChild(document.createTextNode(mark.textContent), mark);
            parent.normalize();
        });
    }
    
    /**
     * Основная функция фильтрации сделок
     */
    function filterDeals() {
        const numberQuery = dealNumberFilter ? dealNumberFilter.value.toLowerCase().trim() : '';
        const creditProductQuery = dealCreditProductFilter ? dealCreditProductFilter.value.toLowerCase().trim() : '';
        const borrowerQuery = dealBorrowerFilter ? dealBorrowerFilter.value.toLowerCase().trim() : '';
        const createdDateFrom = dealCreatedDateFromInput ? dealCreatedDateFromInput.value : '';
        const createdDateTo = dealCreatedDateToInput ? dealCreatedDateToInput.value : '';
        
        console.log('Фильтрация сделок:', {
            number: numberQuery,
            creditProduct: creditProductQuery,
            borrower: borrowerQuery,
            createdFrom: createdDateFrom,
            createdTo: createdDateTo
        });

        const dealCards = dealsContainer.querySelectorAll('.deal-card');
        let visibleCount = 0;

        dealCards.forEach(card => {
            // Сначала убираем подсветку
            removeDealHighlight(card);
            
            // Получаем данные из data-атрибутов
            const dealNumber = card.getAttribute('data-deal-number') || '';
            const dealCreditProduct = card.getAttribute('data-deal-credit-product') || '';
            const dealBorrowers = card.getAttribute('data-deal-borrowers') || '';
            const dealCreated = card.getAttribute('data-deal-created') || '';

            // Проверяем соответствие фильтрам
            let matches = true;

            // Фильтр по номеру
            if (numberQuery && !dealNumber.includes(numberQuery)) {
                matches = false;
            }

            // Фильтр по кредитному продукту
            if (creditProductQuery && !dealCreditProduct.includes(creditProductQuery)) {
                matches = false;
            }

            // Фильтр по должнику
            if (borrowerQuery && !dealBorrowers.includes(borrowerQuery)) {
                matches = false;
            }

            // Фильтр по дате создания
            if (createdDateFrom && dealCreated && dealCreated < createdDateFrom) {
                matches = false;
            }
            if (createdDateTo && dealCreated && dealCreated > createdDateTo) {
                matches = false;
            }

            // Показываем/скрываем карточку
            if (matches) {
                card.style.display = 'block';
                visibleCount++;
                
                // Применяем подсветку для видимых карточек
                if (numberQuery.length >= 2) {
                    // Подсвечиваем номер сделки в правой части карточки
                    const textEndDiv = card.querySelector('.text-end');
                    if (textEndDiv) {
                        const smallElements = textEndDiv.querySelectorAll('small');
                        smallElements.forEach(el => {
                            // Ищем элемент с номером сделки (после "| Номер")
                            if (el.classList.contains('fw-bold') && el.textContent.trim()) {
                                const prevElement = el.previousElementSibling;
                                if (prevElement && prevElement.textContent.includes('Номер')) {
                                    highlightDealText(el, numberQuery);
                                }
                            }
                        });
                    }
                }
                
                if (borrowerQuery.length >= 2) {
                    const borrowerElements = card.querySelectorAll('.badge.bg-light');
                    borrowerElements.forEach(el => {
                        const parentDiv = el.closest('div');
                        if (parentDiv && parentDiv.innerHTML.includes('Должник:')) {
                            highlightDealText(el, borrowerQuery);
                        }
                    });
                }
            } else {
                card.style.display = 'none';
            }
        });

        console.log(`Показано сделок: ${visibleCount} из ${dealCards.length}`);
    }

    /**
     * Сброс всех фильтров сделок
     */
    function resetDealFilters() {
        if (dealNumberFilter) dealNumberFilter.value = '';
        if (dealCreditProductFilter) dealCreditProductFilter.value = '';
        if (dealBorrowerFilter) dealBorrowerFilter.value = '';
        if (dealCreatedDateFromInput) dealCreatedDateFromInput.value = '';
        if (dealCreatedDateToInput) dealCreatedDateToInput.value = '';

        
        // Убираем подсветку со всех карточек
        const dealCards = dealsContainer.querySelectorAll('.deal-card');
        dealCards.forEach(card => {
            removeDealHighlight(card);
            card.style.display = 'block';
        });
        
        console.log('Фильтры сделок сброшены');
    }

    // Добавляем обработчики событий для сделок
    if (dealNumberFilter) {
        dealNumberFilter.addEventListener('input', filterDeals);
    }
    if (dealCreditProductFilter) {
        dealCreditProductFilter.addEventListener('change', filterDeals);
    }
    if (dealBorrowerFilter) {
        dealBorrowerFilter.addEventListener('input', filterDeals);
    }
    if (dealCreatedDateFromInput) {
        dealCreatedDateFromInput.addEventListener('change', filterDeals);
    }
    if (dealCreatedDateToInput) {
        dealCreatedDateToInput.addEventListener('change', filterDeals);
    }
    if (resetDealButton) {
        resetDealButton.addEventListener('click', resetDealFilters);
    }
});

/* =====================================================================
   ПОИСК ПО ИНН - ФУНКЦИОНАЛЬНОСТЬ
   ===================================================================== */

/**
 * Обработка поиска по ИНН
 * Уже реализовано в шаблонах, этот раздел для будущих улучшений
 */
document.addEventListener('DOMContentLoaded', function() {
    // Код для поиска по ИНН уже находится в шаблонах
    // Здесь можно добавить дополнительную функциональность
});