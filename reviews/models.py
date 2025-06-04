from django.db import models
from django.urls import reverse
from ckeditor.fields import RichTextField
from django_ckeditor_5.fields import CKEditor5Field
# включая новую модель


class Rubric(models.Model):
    """
    Модель Рубрики.
    """
    name = models.CharField(max_length=200, verbose_name='Наименование', null=False, blank=False)  # наименование рубрики
    slug = models.SlugField(max_length=200, db_index=True)

    class Meta:
        ordering = ['name']  # сортировка по имени
        verbose_name = 'Рубрика'  # Наименование в ед. Числе
        verbose_name_plural = 'Рубрики'  # Наименование в мн. Числе

    def __str__(self):
        return self.name


class Category(models.Model):
    """
    Модель Категории.
    """
    name = models.CharField(max_length=200, verbose_name='Наименование', null=False, blank=False)  # наименование категории
    slug = models.SlugField(max_length=200, db_index=True)

    class Meta:
        ordering = ['name']  # сортировка по имени
        verbose_name = 'Категория'  # Наименование в ед. Числе
        verbose_name_plural = 'Категории'  # Наименование в мн. Числе

    def __str__(self):
        return self.name


class Review(models.Model):
    """
    Модель Обзоры.
    """
    class Power(models.TextChoices):
        DRAFT = 'Опубликован', 'Опубликован'
        USE = 'Применяется с', 'Применяется с'
        TAKE_EFFECT = 'Вступает в силу', 'Вступает в силу'

    title = models.CharField(max_length=200, verbose_name='Заголовок', null=False, blank=False)  # наименование
    name = models.TextField(verbose_name='Название', null=False, blank=False)  # описание
    description = CKEditor5Field(verbose_name='Полное описание', config_name='extends')
    link = models.URLField(verbose_name='ссылка', null=False, blank=False)  # ссылка
    powers = models.CharField(max_length=200, verbose_name='статус', null=True, blank=True, choices=Power.choices, default=Power.DRAFT)  # статус
    power_date = models.DateField(verbose_name='дата статуса', null=True, blank=True)  # дата статуса
    current_date = models.DateField(verbose_name='текущая дата', null=False, blank=False, auto_now=True)  # дата создания (текущая дата)
    category = models.ForeignKey(Category, null=False, on_delete=models.PROTECT, verbose_name='категория')  # категория (связка с категориями)
    rubric = models.ManyToManyField(Rubric, verbose_name='рубрика')
    publication_date = models.DateField(verbose_name='дата публикации в оф. источнике', null=False, blank=False,default=None)


    class Meta:
        ordering = ['-current_date']  # сортировка по имени
        verbose_name = 'Обзор'  # Наименование в ед. Числе
        verbose_name_plural = 'Обзоры'  # Наименование в мн. Числе

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('reviews:review_detal', args=[self.pk])
