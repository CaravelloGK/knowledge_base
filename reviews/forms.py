from django import forms
from .models import Review, Category, Rubric
from django.forms import ModelForm
from django_ckeditor_5.widgets import CKEditor5Widget
# включая редактор


class SearchForm(forms.Form):
    """
    Форма для поиска
    """
    query = forms.CharField(
        label='Поиск',  # указываем лейбл
        max_length=200,  # указываем максисалью длину
        required=False,  # указываем, что поле не обязательно к заполнению
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Поиск...',  # указываем плейсхолдер
                "class": "form-control"  # указываем bootstrap класс
            }))


class ReviewForm(forms.ModelForm):
    """
    Форма для создания и редактирования обзора
    """
    powers_option = {
        None: 'выбери статус',
        'Применяется с': 'Применяется с',
        'Вступает в силу': 'Вступает в силу'
    }

    # далее задаем настройки полей формы
    title = forms.CharField(label='Заголовок:', required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    name = forms.CharField(label='Название:',
                           widget=forms.Textarea(attrs={"class": "form-control", "rows": "1"}),
                           required=True)
    description = forms.CharField(label='Описание:',
                                  widget=CKEditor5Widget(
                                      attrs={"class": "django_ckeditor_5"}, config_name="extends"),
                                  required=True)
    link = forms.URLField(label='Название:', required=True, widget=forms.URLInput(attrs={"class": "form-control"}))
    powers = forms.ChoiceField(label='Статус', widget=forms.Select(attrs={"class": "form-control"}),
                               required=False, choices=powers_option)
    power_date = forms.DateField(label='Дата статуса:',
                                 widget=forms.DateInput(format='%d.%m.%Y',
                                                        attrs={"class": "form-control",
                                                               "type": "date"}),
                                 input_formats=['%d.%m.%Y'],
                                 initial=None,
                                 required=False)

    category = forms.ModelChoiceField(label='Категория',
                                      required=True,
                                      empty_label='выбери категорию',
                                      queryset=Category.objects.all(),
                                      widget=forms.Select(attrs={"class": "form-control"}),
                                      )

    rubric = forms.ModelMultipleChoiceField(label='Рубрика',
                                            required=True,
                                            queryset=Rubric.objects.all(),
                                            widget=forms.CheckboxSelectMultiple(),
                                            )

    publication_date = forms.DateField(label='Дата публикации в оф. источнике:',
                                 widget=forms.DateInput(format='%d.%m.%Y',
                                                        attrs={"class": "form-control",
                                                               "type": "date"}),
                                 input_formats=['%d.%m.%Y'],
                                 initial=None,
                                 required=True)

    # метод для связывания модели с формой
    class Meta:
        model = Review
        fields = ['title', 'name', 'description', 'link', 'powers', 'power_date', 'category', 'rubric', 'publication_date']


class EmailPostForm(forms.Form):
    """
    Форма для отправки 1 записи
    """
    email = forms.CharField(label='Кому', required=True,
                            widget=forms.TextInput(
                                 attrs={
                                     'placeholder': 'Введите email через запятую',
                                     'class': 'form-control'
                                 }
                            ))
    comment = forms.CharField(label='Комментарии:',
                              widget=forms.Textarea(attrs={"class": "form-control", "rows": "5"}),
                              required=False)


class RecommendMultipleForm(forms.Form):
    reviews = forms.ModelMultipleChoiceField(
        label='Выберите обзоры',
        queryset=Review.objects.none(),  # Пустой queryset, будет переопределен в представлении
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input-reviews'})
    )


class LoginForm(forms.Form):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
