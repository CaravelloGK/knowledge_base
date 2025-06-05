from django.db import models
from django.core.validators import RegexValidator
from django.urls import reverse


class LegalEntity(models.Model):
    # Модель Юридические лица
    name = models.CharField(max_length=255, verbose_name="Название")
    inn = models.CharField(
        max_length=12,
        verbose_name='ИНН',
        validators=[
            RegexValidator(
                regex='^(\d{10}|\d{12})$',
                message='ИНН должен содержать 10 или 12 цифр',
            )
        ]
    )
    ogrn = models.CharField(
        max_length=13,
        verbose_name='ОГРН',
        validators=[
            RegexValidator(
                regex='^\d{13}$',
                message='ОГРН должен содержать 13 цифр',
            )
        ]
    )
    legal_form = models.TextField(verbose_name='Организационно-правовая форма')
    company_group = models.TextField(verbose_name='Группа компаний')
    status = models.TextField(verbose_name='Статус')
    authorized_capital = models.TextField(verbose_name='Уставной капитал')

    # Необязательные поля
    registrar = models.TextField(verbose_name='Реестродержатель', blank=True, null=True)
    registrar_inn = models.CharField(
        max_length=12,
        verbose_name='ИНН реестродержателя',
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex='^(\d{10}|\d{12})$',
                message='ИНН должен содержать 10 или 12 цифр',
            )
        ]
    )

    # Поля дат
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return f"{self.name} (ИНН: {self.inn})"

    def get_absolute_url(self):
        return reverse('legal_opin:legal_entity_detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['-updated_at']
        verbose_name = "Юридическое лицо"
        verbose_name_plural = "Юридические лица"


class ExecutiveBody(models.Model):
    # Модель Единоличный исполнительный орган
    legal_entity = models.ForeignKey(
        LegalEntity,
        on_delete=models.CASCADE,
        related_name='executive_bodies',
        verbose_name='Юридическое лицо'
    )
    name = models.TextField(verbose_name='Имя/Наименование')
    inn = models.CharField(
        max_length=12,
        verbose_name='ИНН',
        validators=[
            RegexValidator(
                regex='^(\d{10}|\d{12})$',
                message='ИНН должен содержать 10 или 12 цифр',
            )
        ]
    )

    def __str__(self):
        return f"{self.name} (ИНН: {self.inn})"

    class Meta:
        verbose_name = 'Единоличный исполнительный орган'
        verbose_name_plural = 'Единоличные исполнительные органы'


class Participant(models.Model):
    # Модель участники/акционеры
    legal_entity = models.ForeignKey(
        LegalEntity,
        on_delete=models.CASCADE,
        related_name='participants',
        verbose_name='Юридическое лицо'
    )
    name = models.TextField(verbose_name='Имя/Наименование')
    inn = models.CharField(
        max_length=12,
        verbose_name='ИНН',
        validators=[
            RegexValidator(
                regex='^(\d{10}|\d{12})$',
                message='ИНН должен содержать 10 или 12 цифр',
            )
        ]
    )
    # Необязательные поля
    share = models.TextField(verbose_name='Доля', blank=True, null=True)
    share_info = models.TextField(verbose_name='Информация о доле', blank=True, null=True)

    def __str__(self):
        return f"{self.name} (ИНН: {self.inn})"

    class Meta:
        verbose_name = 'Участник'
        verbose_name_plural = 'Участники'


class Deal(models.Model):
    # Модель сделки
    number = models.TextField(verbose_name='Номер')
    date = models.DateField(verbose_name='Дата')
    credit_product_type = models.TextField(verbose_name='Вид кредитного продукта')
    legal_entities = models.ManyToManyField(
        LegalEntity,
        related_name='deals',
        verbose_name='Юридические лица'
    )

    def __str__(self):
        return f"Сделка {self.number} от {self.date}"

    class Meta:
        verbose_name = 'Сделка'
        verbose_name_plural = 'Сделки'