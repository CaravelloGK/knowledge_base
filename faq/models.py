from django.db import models
from django.urls import reverse
from ckeditor.fields import RichTextField
from django_ckeditor_5.fields import CKEditor5Field


class Direction_of_business(models.Model):
    # направление бизнеса
    name = models.CharField(max_length=100, verbose_name="Название бизнеса")
    description = models.TextField(blank=True, verbose_name="Описание")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Направления бизнеса"
        verbose_name_plural = "Направления бизнеса"


class Section(models.Model):
    # рубрики
    name = models.CharField(max_length=100, verbose_name="Название рубрики")
    description = models.TextField(blank=True, verbose_name="Описание")
    global_section = models.ForeignKey(Direction_of_business, on_delete=models.CASCADE,
                                       verbose_name="Направление бизнеса")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Рубрика"
        verbose_name_plural = "Рубрики"


class Question(models.Model):
    direction_of_business = models.ForeignKey(Direction_of_business, on_delete=models.CASCADE,
                                       verbose_name="Направление бизнеса")
    Section = models.ForeignKey(Section, on_delete=models.CASCADE,
                                       verbose_name="Рубрика")
    question = models.TextField(verbose_name="Вопрос", null=False, blank=False,)
    answer = CKEditor5Field(verbose_name='Ответ', config_name='extends')
    document = models.FileField(upload_to="documents/", null=True, blank=True, verbose_name="Документ")

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        return self.question