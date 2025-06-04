from django.db import models
from django.urls import reverse
from ckeditor.fields import RichTextField
from django_ckeditor_5.fields import CKEditor5Field


class Direction(models.Model):
    """
    Направление деятельности Банка, свойственное риску.
    """
    name = models.CharField(max_length=200, verbose_name='Наименование', null=False, blank=False)  # наименование направления
    slug = models.SlugField(max_length=200, db_index=True)

    class Meta:
        ordering = ['name']  # сортировка по имени
        verbose_name = 'Направление деятельности Банка'  # Наименование в ед. Числе
        verbose_name_plural = 'Направления деятельности Банка'  # Наименование в мн. Числе

    def __str__(self):
        return self.name


class Kind(models.Model):
    """
    Вид правовой экспертизы.
    """
    name = models.CharField(max_length=200, verbose_name='Вид правовой экспертизы', null=False, blank=False)  # наименование вида
    slug = models.SlugField(max_length=200, db_index=True)

    class Meta:
        ordering = ['name']  # сортировка по имени
        verbose_name = 'Вид правовой экспертизы'  # Наименование в ед. Числе
        verbose_name_plural = 'Виды правовой экспертизы'  # Наименование в мн. Числе

    def __str__(self):
        return self.name


class Subject(models.Model):
    """
    Предмет правового анализа.
    """
    name = models.CharField(max_length=200, verbose_name='Наименование', null=False,
                            blank=False)  # наименование предмета правового анализа
    slug = models.SlugField(max_length=200, db_index=True)

    class Meta:
        ordering = ['name']  # сортировка по имени
        verbose_name = 'Предмет правового анализа'  # Наименование в ед. Числе
        verbose_name_plural = 'Предметы правового анализа'  # Наименование в мн. Числе

    def __str__(self):
        return self.name


class Risk(models.Model):
    """
    Риск.
    """
    direction = models.ForeignKey(Direction, null=False, on_delete=models.PROTECT,
                                  verbose_name='Направление деятельности Банка, свойственное риску')  # категория (связка с категориями)
    kind = models.ForeignKey(Kind, null=False, on_delete=models.PROTECT,
                             verbose_name='Вид правовой экспертизы')  # категория (связка с категориями)
    subject = models.ForeignKey(Subject, null=False, on_delete=models.PROTECT,
                                verbose_name='Предмет правового анализа')  # категория (связка с категориями)
    risk = models.TextField(verbose_name='Риск', null=False, blank=False)  # Риск
    risk_factor = CKEditor5Field(verbose_name='Риск-факторы', config_name='extends')  # Риск-факторы
    legal_basis = CKEditor5Field(verbose_name='Правовое обоснование', config_name='extends')  # Правовое обоснование
    negative_consequences = CKEditor5Field(verbose_name='Негативные последствия',
                                           config_name='extends')  # Негативные последствия
    minimization_measures = CKEditor5Field(verbose_name='Меры минимизации', config_name='extends')  # Меры минимизации
    associated_risks = models.TextField(verbose_name='Связанные риски', null=False, blank=False)  # Связанные рискиa
    info_about_risk_realization = CKEditor5Field(verbose_name='Информация о реализации риска',
                                                 null=False,
                                                 blank=False,
                                                 config_name='extends')  # Информация о реализации риска

    class Meta:
        ordering = ['risk']  # сортировка по имени
        verbose_name = 'Риск'  # Наименование в ед. Числе
        verbose_name_plural = 'Риски'  # Наименование в мн. Числе

    def __str__(self):
        return self.risk

    def get_absolute_url(self):
        return reverse('risk:risk_detal', args=[self.pk])