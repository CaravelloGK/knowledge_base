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