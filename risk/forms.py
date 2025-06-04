from django import forms
from django.forms import ModelForm
from .models import Risk, Direction, Kind, Subject
from django_ckeditor_5.widgets import CKEditor5Widget


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


class RiskForm(forms.ModelForm):
    """
    Форма для создания и редактирования риска
    """
    direction = forms.ModelChoiceField(label='Направление деятельности Банка',
                                       required=True,
                                       empty_label='выбери направление деятельности Банка',
                                       queryset=Direction.objects.all(),
                                       widget=forms.Select(attrs={"class": "form-control"}),
                                       )

    kind = forms.ModelChoiceField(label='Вид правовой экспертизы',
                                  required=True,
                                  empty_label='выбери вид правовой экспертизы',
                                  queryset=Kind.objects.all(),
                                  widget=forms.Select(attrs={"class": "form-control"}),
                                  )

    subject = forms.ModelChoiceField(label='Предмет правового анализа',
                                     required=True,
                                     empty_label='выбери предмет правового анализа',
                                     queryset=Subject.objects.all(),
                                     widget=forms.Select(attrs={"class": "form-control"}),
                                     )

    risk = forms.CharField(label='Риск:',
                           widget=forms.Textarea(attrs={"class": "form-control", "rows": "1"}),
                           required=True)

    risk_factor = forms.CharField(label='Риск-факторы:',
                                  widget=CKEditor5Widget(
                                      attrs={"class": "django_ckeditor_5"}, config_name="extends"),
                                  required=True)

    legal_basis = forms.CharField(label='Правовое обоснование:',
                                  widget=CKEditor5Widget(
                                      attrs={"class": "django_ckeditor_5"}, config_name="extends"),
                                  required=True)

    negative_consequences = forms.CharField(label='Негативные последствия:',
                                            widget=CKEditor5Widget(
                                                attrs={"class": "django_ckeditor_5"}, config_name="extends"),
                                            required=True)

    minimization_measures = forms.CharField(label='Меры минимизации и существующие контрольные мероприятия:',
                                            widget=CKEditor5Widget(
                                                attrs={"class": "django_ckeditor_5"}, config_name="extends"),
                                            required=True)

    associated_risks = forms.CharField(label='Связанные риски:',
                                       widget=forms.Textarea(attrs={"class": "form-control", "rows": "1"}),
                                       required=True)

    info_about_risk_realization = forms.CharField(label='Информация о реализации риска:',
                                                  widget=CKEditor5Widget(
                                                      attrs={"class": "django_ckeditor_5"}, config_name="extends"),
                                                  required=True)

    # метод для связывания модели с формой
    class Meta:
        model = Risk
        fields = ['direction', 'kind', 'subject', 'risk', 'risk_factor', 'legal_basis', 'negative_consequences', 'minimization_measures', 'associated_risks', 'info_about_risk_realization']



class Export_filters(forms.Form):
    direction = forms.ModelChoiceField(label='Направление деятельности Банка',
                                       required=False,
                                       empty_label='выбери направление деятельности Банка',
                                       queryset=Direction.objects.all(),
                                       widget=forms.Select(attrs={"class": "form-control"}),
                                       )

    kind = forms.ModelChoiceField(label='Вид правовой экспертизы',
                                  required=False,
                                  empty_label='выбери вид правовой экспертизы',
                                  queryset=Kind.objects.all(),
                                  widget=forms.Select(attrs={"class": "form-control"}),
                                  )

    subject = forms.ModelChoiceField(label='Предмет правового анализа',
                                     required=False,
                                     empty_label='выбери предмет правового анализа',
                                     queryset=Subject.objects.all(),
                                     widget=forms.Select(attrs={"class": "form-control"}),
                                     )