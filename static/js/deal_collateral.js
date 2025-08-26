document.addEventListener('DOMContentLoaded', function() {

    // Основные функции

    // функция отвечает за автовысоту тектовых блоков (textarea)
    function adjustTextareaHeight(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = `${textarea.scrollHeight}px`;
    }

    // функция отвечает за автовысоту тектовых блоков (textarea) на входные данные и ручной ввод
    function processAllTextareas() {
        document.querySelectorAll('.form-control.textarea').forEach(textarea => {
            textarea.rows = 1;

            if (textarea.value) {
                adjustTextareaHeight(textarea);
            }

            textarea.addEventListener('input', function() {
                adjustTextareaHeight(this);
            });
        });
    }



    // Инициализация всех функций
    function init() {
        processAllTextareas();
    }

    init();
});