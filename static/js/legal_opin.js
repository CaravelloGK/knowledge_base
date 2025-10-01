document.addEventListener('DOMContentLoaded', function() {

    // Основные функции

    // Функция отвечает за скрытие - отображение доп. полей к риск-факторам
    function toggleTextareaVisibility() {
        document.querySelectorAll('.toggle-textarea').forEach(function(checkbox) {
            const targetId = checkbox.dataset.target;
            const textarea = document.getElementById(targetId);
            if (!textarea) return;

            const wrapper = textarea.closest('.fieldWrapper') || textarea.parentElement;

            const toggleVisibility = () => {
                const isVisible = checkbox.checked;
                wrapper.style.display = isVisible ? 'block' : 'none';
                textarea.style.display = isVisible ? 'block' : 'none';
            };

            toggleVisibility();
            checkbox.addEventListener('change', toggleVisibility);
        });
    }

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

    // функция отвечает за скрытие полей реестродержатель и ИНН реестродержателя если ОПФ - ООО
    function handleLegalFormVisibility() {
        const opf = document.getElementById('id_legal_form');
        const reestr = document.getElementById('div_id_registrar');
        const reestrInn = document.getElementById('div_id_registrar_inn');

        if (!opf || !reestr || !reestrInn) return;

        const toggleVisibility = () => {
            const isOOO = opf.value === 'ООО';
            reestr.style.display = isOOO ? 'none' : 'block';
            reestrInn.style.display = isOOO ? 'none' : 'block';
        };

        toggleVisibility();
        opf.addEventListener('change', toggleVisibility);
    }

    // функция отвечает за блок закупки
    function handlePurchases() {
        const zakupkiCheck = document.getElementById('id_zakup');
        const zakupkiInf = document.getElementById('id_laws_zakup');
        const zakupkiVin = document.getElementById('div_id_zakup_win');
        const zakupkiBlock = document.getElementById('div_id_laws_zakup');

        if (!zakupkiCheck || !zakupkiInf || !zakupkiVin || !zakupkiBlock) return;

        const toggleVisibility = () => {
            const isChecked = zakupkiCheck.checked;
            const value = zakupkiInf.value;
            const isValidValue = ['44-ФЗ', '223-ФЗ', '44-ФЗ и 223-ФЗ'].includes(value);

            zakupkiVin.style.display = isChecked && isValidValue ? 'block' : 'none';
            zakupkiBlock.style.display = isChecked && isValidValue ? 'block' : 'none';
        };

        toggleVisibility();
        zakupkiCheck.addEventListener('change', toggleVisibility);
        zakupkiInf.addEventListener('change', toggleVisibility);
    }

    // функция отвечает за отчистку форм коллегиальных органов
    function clearForm(formIndex) {
        const form = document.getElementById(`collegial_form_${formIndex}`);
        if (!form) return;

        form.querySelectorAll('input:not([type=radio]):not([type=checkbox]):not([type=button]):not([type=submit]):not([type=reset]), textarea, select')
            .forEach(input => input.value = '');

        form.querySelectorAll('input[type=checkbox], input[type=radio]')
            .forEach(checkbox => checkbox.checked = false);
    }

    // функция отвечает за блок коллегиальные органы
    function handleCollegialForms() {
        const form0Value = document.getElementById('id_collegial-0-governing_bodies')?.value;
        const form1Value = document.getElementById('id_collegial-1-governing_bodies')?.value;
        const form0 = document.getElementById('collegial_form_0');
        const form1 = document.getElementById('collegial_form_1');

        const selectFirstOptionIfEmpty = (formIndex) => {
            const form = document.getElementById(`collegial_form_${formIndex}`);
            if (!form) return;
            const idInput = form.querySelector('input[name$="-id"]');
            const hasDbId = !!(idInput && idInput.value);
            if (hasDbId) return; // существующую запись не трогаем
            const select = form.querySelector('select[name$="-governing_bodies"]');
            if (!select) return;
            if (!select.value) {
                const first = Array.from(select.options).find(o => o.value);
                if (first) {
                    select.value = first.value;
                    // уведомим слайдер о смене
                    select.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }
        };

        const updateForms = () => {
            const value = document.querySelector('input[name="collegial_count"]:checked')?.value;

            if (value === '0') {
                if (form0) form0.style.display = 'none';
                if (form1) form1.style.display = 'none';
                clearForm(0);
                clearForm(1);
            } else if (value === '1') {
                if (form0) form0.style.display = 'block';
                if (form1) form1.style.display = 'none';
                clearForm(1);
                // При первом показе формы-0 выберем значение по умолчанию
                selectFirstOptionIfEmpty(0);
            } else if (value === '2') {
                if (form0) form0.style.display = 'block';
                if (form1) form1.style.display = 'block';
                // При первом показе выберем значения по умолчанию
                selectFirstOptionIfEmpty(0);
                selectFirstOptionIfEmpty(1);
            }
        };

        // Функция проверки заполненности формы
        const hasFormData = (formIndex) => {
            const form = document.getElementById(`collegial_form_${formIndex}`);
            if (!form) return false;
            
            const inputs = form.querySelectorAll('input:not([type=radio]):not([type=checkbox]):not([type=button]):not([type=submit]):not([type=reset]), textarea, select');
            const hasValue = Array.from(inputs).some(input => input.value.trim() !== '');
            
            const deleteCheckbox = form.querySelector('input[name$="-DELETE"]');
            return hasValue && (!deleteCheckbox || !deleteCheckbox.checked);
        };

        // Функция показа предупреждения
        const showWarning = (message) => {
            // Создаем модал предупреждения
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header bg-warning text-dark">
                            <h5 class="modal-title">
                                <i class="fas fa-exclamation-triangle me-2"></i>
                                Внимание!
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p class="mb-0">${message}</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Понятно</button>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            
            // Показываем модал
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
            
            // Удаляем модал после скрытия
            modal.addEventListener('hidden.bs.modal', () => {
                document.body.removeChild(modal);
            });
        };

        // Функция проверки безопасности изменения количества
        const checkSafeChange = (newValue, oldValue) => {
            if (newValue >= oldValue) return true; // Увеличение - безопасно
            
            // Проверяем, есть ли заполненные данные в формах, которые будут скрыты
            if (newValue === '0' && (hasFormData(0) || hasFormData(1))) {
                showWarning('У вас есть заполненные данные в коллегиальных органах. Если хотите уменьшить количество органов, используйте кнопку "Удалить орган" для каждого органа отдельно.');
                return false;
            }
            
            if (newValue === '1' && oldValue === '2' && hasFormData(1)) {
                showWarning('Во втором коллегиальном органе есть заполненные данные. Если хотите убрать его, используйте кнопку "Удалить орган".');
                return false;
            }
            
            return true;
        };

        // Инициализация с учетом пометок DELETE (живые = имеющие id и не помеченные на удаление)
        const del0 = document.querySelector('input[name="collegial-0-DELETE"]')?.checked;
        const del1 = document.querySelector('input[name="collegial-1-DELETE"]')?.checked;
        
        // Считаем только органы с id (существующие в БД) и не помеченные на удаление
        const alive = (document.querySelector('input[name="collegial-0-id"]')?.value && !del0 ? 1 : 0)
                    + (document.querySelector('input[name="collegial-1-id"]')?.value && !del1 ? 1 : 0);

        if (alive >= 2) {
            document.getElementById('collegial_count_2').checked = true;
        } else if (alive === 1) {
            document.getElementById('collegial_count_1').checked = true;
        } else {
            document.getElementById('collegial_count_0').checked = true;
        }

        updateForms();

        // Обработчики для радиокнопок с защитой от потери данных
        let previousValue = document.querySelector('input[name="collegial_count"]:checked')?.value || '0';
        
        document.querySelectorAll('input[name="collegial_count"]').forEach(radio => {
            radio.addEventListener('change', function() {
                const newValue = this.value;
                
                if (checkSafeChange(newValue, previousValue)) {
                    updateForms();
                    previousValue = newValue;
                } else {
                    // Возвращаем предыдущее значение
                    document.querySelector(`input[name="collegial_count"][value="${previousValue}"]`).checked = true;
                }
            });
        });

        // Функция синхронизации радио с количеством активных органов
        const syncRadioWithActiveCount = () => {
            const del0 = document.querySelector('input[name="collegial-0-DELETE"]')?.checked;
            const del1 = document.querySelector('input[name="collegial-1-DELETE"]')?.checked;
            
            // Считаем только органы с id (существующие в БД) и не помеченные на удаление
            const alive = (document.querySelector('input[name="collegial-0-id"]')?.value && !del0 ? 1 : 0)
                        + (document.querySelector('input[name="collegial-1-id"]')?.value && !del1 ? 1 : 0);
            
            if (alive >= 2) {
                document.getElementById('collegial_count_2').checked = true;
                previousValue = '2';
            } else if (alive === 1) {
                document.getElementById('collegial_count_1').checked = true;
                previousValue = '1';
            } else {
                document.getElementById('collegial_count_0').checked = true;
                previousValue = '0';
            }
        };

        // Делаем функцию доступной глобально для вызова из шаблона
        window.syncRadioWithActiveCount = syncRadioWithActiveCount;
    }

    // функция отвечает за блок 67,1
    function handleConfirmationProcedure() {
        const legalFormInput = document.getElementById('id_legal_form');
        const textarea = document.getElementById('id_confirmation_procedure_dop_info');

        if (!legalFormInput) return;

        const updateProcedure = () => {
            const legalFormValue = legalFormInput.value;
            const checkboxes = document.querySelectorAll('input[name="confirmation_procedure"]');
            const inoeCheckbox = document.getElementById('id_confirmation_procedure_6');
            const sposob = document.getElementById('id_sposob_vibor');
            if (inoeCheckbox && textarea) {
                const toggleTextarea = () => {
                    textarea.style.display = inoeCheckbox.checked ? 'block' : 'none';
                };

                toggleTextarea();
                inoeCheckbox.addEventListener('change', toggleTextarea);
            }
            if (legalFormValue === 'АО' || legalFormValue === 'ПАО') {
                checkboxes.forEach(checkbox => {
                    checkbox.checked = true;
                    checkbox.disabled = true;
                });
                sposob.value = 'Закон'
                if (textarea) textarea.style.display = 'none';
            }
            // else if (legalFormValue === 'ООО') {
            //     // checkboxes.forEach(checkbox => {
            //     //     checkbox.checked = false;
            //     //     checkbox.disabled = false;
            //     // });
            //
            //     if (inoeCheckbox && textarea) {
            //         const toggleTextarea = () => {
            //             textarea.style.display = inoeCheckbox.checked ? 'block' : 'none';
            //         };
            //
            //         toggleTextarea();
            //         inoeCheckbox.addEventListener('change', toggleTextarea);
            //     }
            // }
        };

        updateProcedure();
        legalFormInput.addEventListener('change', updateProcedure);
    }

    // Инициализация всех функций
    function init() {
        toggleTextareaVisibility();
        processAllTextareas();
        handleLegalFormVisibility();
        handlePurchases();
        handleCollegialForms();
        // if (window.myVar) {
        handleConfirmationProcedure();
        // }
    }

    init();
});