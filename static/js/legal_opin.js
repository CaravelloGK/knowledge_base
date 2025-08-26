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
            } else if (value === '2') {
                if (form0) form0.style.display = 'block';
                if (form1) form1.style.display = 'block';
            }
        };

        // Инициализация
        if (form0Value && form1Value) {
            document.getElementById('collegial_count_2').checked = true;
        } else if (form0Value || form1Value) {
            document.getElementById('collegial_count_1').checked = true;
            if (form0Value) {
                clearForm(1);
            } else {
                clearForm(0);
            }
        } else {
            document.getElementById('collegial_count_0').checked = true;
            clearForm(0);
            clearForm(1);
        }

        updateForms();

        // Обработчики для радиокнопок
        document.querySelectorAll('input[name="collegial_count"]').forEach(radio => {
            radio.addEventListener('change', updateForms);
        });
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