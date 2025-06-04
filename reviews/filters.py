import django_filters
from django import forms
from .models import Review, Category, Rubric
from django.utils.translation import gettext_lazy as _


class ReviewFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(
        field_name='current_date',
        lookup_expr='gte',
        label='Дата начала',
        widget=forms.widgets.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    end_date = django_filters.DateFilter(
        field_name='current_date',
        lookup_expr='lte',
        label='Дата окончания',
        widget=forms.widgets.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    category = django_filters.ModelChoiceFilter(
        field_name='category',
        queryset=Category.objects.all(),
        label='Категория',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    rubric = django_filters.ModelChoiceFilter(
        field_name='rubric',
        queryset=Rubric.objects.all(),
        label='Рубрика',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = Review
        fields = ['start_date', 'end_date', 'category', 'rubric']