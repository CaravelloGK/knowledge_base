from django import forms
from .models import Doc_class, Section, Direction, Direction_of_business, Document
from django_ckeditor_5.widgets import CKEditor5Widget


class SearchForm(forms.Form):
    """
    Форма для поиска
    """
    query = forms.CharField(
        max_length=200,  # указываем максисалью длину
        required=False,  # указываем, что поле не обязательно к заполнению
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Поиск...',  # указываем плейсхолдер
                "class": "form-control search-field"  # указываем bootstrap класс
            }))
    directional = forms.CharField(widget=forms.HiddenInput(), required=False)


class DocumentForm(forms.ModelForm):

    title = forms.CharField(label='Название', required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    file = forms.FileField(label='Файл документа', required=False, widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'accept': '.pdf, .docx, .pptx,'
        }
    ))
    created_at = forms.DateField(label='Дата статуса:',
                                 widget=forms.DateInput(format='%Y-%m-%d',
                                                        attrs={"class": "form-control",
                                                               "type": "date"}),
                                 initial=None,
                                 required=False)
    updated_at = forms.DateField(label='Дата статуса:',
                                 widget=forms.DateInput(format='%Y-%m-%d',
                                                        attrs={"class": "form-control",
                                                               "type": "date"}),
                                 initial=None,
                                 required=False)
    global_section = forms.ModelChoiceField(label='Направление бизнеса',
                                            required=True,
                                            empty_label='Выбери направление бизнеса',
                                            queryset=Direction_of_business.objects.all(),
                                            widget=forms.Select(attrs={"class": "form-control"}),
                                            )
    section = forms.ModelChoiceField(label='Направление',
                                     required=False,
                                     empty_label='Выбери направление',
                                     queryset=Direction.objects.all(),
                                     widget=forms.Select(attrs={"class": "form-control"}),
                                     )
    category = forms.ModelChoiceField(label='Рубрика',
                                      required=True,
                                      empty_label='Выбери рубрику',
                                      queryset=Section.objects.all(),
                                      widget=forms.Select(attrs={"class": "form-control"}),
                                      )
    subcategory = forms.ModelChoiceField(label='Тип документа',
                                         required=True,
                                         empty_label='Выбери тип документа',
                                         queryset=Doc_class.objects.all(),
                                         widget=forms.Select(attrs={"class": "form-control"}),
                                         )
    is_template = forms.BooleanField(label='Это шаблон', required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
    description = forms.CharField(label='Описание:',
                                  widget=CKEditor5Widget(
                                      attrs={"class": "django_ckeditor_5"}, config_name="extends"),
                                  required=False)

    # метод для связывания модели с формой
    class Meta:
        model = Document
        fields = ['title', 'file', 'global_section', 'section', 'category', 'subcategory', 'is_template', 'description']