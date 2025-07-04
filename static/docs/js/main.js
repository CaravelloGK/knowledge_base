document.addEventListener('DOMContentLoaded', function() {
    // Сохраняем все карточки при первой загрузке
    const row = document.querySelector('.docs-page .row.g-3');
    if (!row) return;
    const allCards = Array.from(row.querySelectorAll('.col-md-6'));
    // Сохраняем копии DOM-элементов (чтобы не терять их при пересборке)
    const allCardsClones = allCards.map(card => card.cloneNode(true));

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
