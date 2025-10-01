/* =====================================================================
   КОПИРОВАНИЕ ИНН / ОГРН В КАРТОЧКЕ ЮЛ
   ===================================================================== */
   document.addEventListener('DOMContentLoaded', function() {
    // Обработчик для кнопок копирования
    document.addEventListener('click', function(e) {
        if (e.target.closest('.copy-btn')) {
            e.preventDefault();
            e.stopPropagation();

            const button = e.target.closest('.copy-btn');
            const textToCopy = button.getAttribute('data-copy');
            const icon = button.querySelector('img.copy-icon');

            // Копируем в буфер обмена
            navigator.clipboard.writeText(textToCopy).then(function() {
                // Показываем успешное копирование
                const originalFilter = icon.style.filter;
                icon.style.filter = 'hue-rotate(90deg) saturate(2)';
                button.classList.add('btn-outline-success');
                button.classList.remove('btn-outline-secondary');

                // Возвращаем исходный вид через 1.5 секунды
                setTimeout(function() {
                    icon.style.filter = originalFilter || '';
                    button.classList.remove('btn-outline-success');
                    button.classList.add('btn-outline-secondary');
                }, 1500);
            }).catch(function(err) {
                console.error('Ошибка при копировании: ', err);
                // Показываем ошибку
                const originalFilter = icon.style.filter;
                icon.style.filter = 'hue-rotate(320deg) saturate(2)';

                setTimeout(function() {
                    icon.style.filter = originalFilter || '';
                }, 1500);
            });
        }
    });
});