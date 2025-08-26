from django.db import models
from django.core.validators import RegexValidator


class LegalEntity(models.Model):
    """
    Модель Юридическое лицо
        имеет обязательные и необязательные поля
    """
    name = models.TextField(verbose_name='Название')    # Наименование Юридического лица - обязательное поле
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
    status = models.TextField(verbose_name='Статус')    # Статус Юридического лица в ЕГРЮЛ (например, действующее, банкроство)
    authorized_capital = models.TextField(verbose_name='Уставной капитал')
    capital_org = models.TextField(verbose_name='Информация о доле, принадлежащей обществу', blank=True, null=True)

    # Необязательные поля

    # Информация о реестродержателе (только для АО/ЗАО/ПАО)
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

    # Дополнительная информация о Юридическом лице
    address = models.TextField(verbose_name='Юрисдикция/местонахождение', default=None)
    info_ustav = models.TextField(verbose_name='Информация о действующей редакии устава', blank=True, null=True, default=None)
    info_ustav_doc = models.TextField(verbose_name='Последние изменения в учредительный документы', blank=True, null=True, default=None)
    info_ustav_doc_dop_info = models.TextField(verbose_name='Учредительные документы: Дополнительная информация/комментарии',
                                                       blank=True, null=True, default=None)
    eio_uchast = models.BooleanField(verbose_name='ЕИО - единственный участник в одном лшице', null=True, default=None)
    corp_dogovor = models.BooleanField(verbose_name='Корпоративный договор', null=True, default=None)
    monopol = models.BooleanField(verbose_name='Субъект естественных монополий', null=True, default=None)
    zastroy = models.BooleanField(verbose_name='Застройщик', null=True, default=None)
    power = models.TextField(verbose_name='Полномочия ОСУ/ОСА', blank=True, null=True, default=None)

    PARTS_GROUPS = {
        'ООО': [
            ('Нотариального подтверждения', 'Нотариального подтверждения'),
            ('Подписания протокола всеми участниками Общества / подписания решения единственным участником', 'Подписания протокола всеми участниками Общества / подписания решения единственным участником'),
            ('Подписания протокола всеми участниками, присутствовавшими на собрании / подписания решения единственным участником', 'Подписания протокола всеми участниками, присутствовавшими на собрании / подписания решения единственным участником',),
            ('Подписания протокола председателем и секретарем собрания', 'Подписания протокола председателем и секретарем собрания'),
            ('С использованием технических средств, позволяющих достоверно установить факт принятия решения', 'С использованием технических средств, позволяющих достоверно установить факт принятия решения'),
            ('Согласно законодательству РФ', 'Согласно законодательству РФ'),
            ('Иное', 'Иное'),
        ],
        'АО': [
            ('Подписания лицом, осуществляющим ведение реестра акционеров и выполняющим функции счетной комиссии', 'Подписания лицом, осуществляющим ведение реестра акционеров и выполняющим функции счетной комиссии'),
            ('Нотариального подтверждения / удостоверения лицом, осуществляющим ведение реестра акционеров и выполняющим функции счетной комиссии', 'Нотариального подтверждения / удостоверения лицом, осуществляющим ведение реестра акционеров и выполняющим функции счетной комиссии'),
        ],
        'ПАО': [
            ('подтверждается лицом, осуществляющим ведение реестра акционеров такого общества и выполняющим функции счетной комиссии',
             'подтверждается лицом, осуществляющим ведение реестра акционеров такого общества и выполняющим функции счетной комиссии'),
        ],
    }
    confirmation_procedure = models.TextField(blank=True, null=True, verbose_name='Способ подтверждения принятия решения')
    confirmation_procedure_dop_info = models.TextField(verbose_name='Способ подтверждения принятия решения: Дополнительная информация/комментарии',
                                                       blank=True, null=True, default=None)

    sposob = (
        ('Устав', 'Устав'),
        ('Решение', 'Решение'),
        ('Закон', 'Закон'),
    )
    sposob_vibor = models.CharField(verbose_name='Указанный способ закреплен', choices=sposob, default=None, blank=True, null=True)

    zakup = models.BooleanField(verbose_name='Заказчик по закупкам', null=True, default=None)
    laws = (
        ('44-ФЗ', '44-ФЗ'),
        ('223-ФЗ', '223-ФЗ'),
        ('44-ФЗ и 223-ФЗ', '44-ФЗ и 223-ФЗ'),
    )
    laws_zakup = models.CharField(verbose_name='Закон по закупкам', choices=laws, default=None, blank=True, null=True)
    zakup_win = models.BooleanField(verbose_name='Победитель по закупке', null=True, default=False)
    judicial_disputes = models.BooleanField(verbose_name='Судебные споры', null=True, default=False)
    judicial_disputes_dop_info = models.TextField(verbose_name='Судебные споры: Дополнительная информация/комментарии', blank=True, null=True,
                                default=None)
    bankrot = models.BooleanField(verbose_name='Банкротство', null=True, default=False)
    bankrot_dop_info = models.TextField(verbose_name='Банкротство: Дополнительная информация/комментарии', blank=True, null=True,
                                default=None)
    enforcement_proceedings = models.BooleanField(verbose_name='Исполнительное производство', null=True, default=False)
    enforcement_proceedings_dop_info = models.TextField(verbose_name='Исполнительное производство: Дополнительная информация/комментарии', blank=True, null=True,
                                default=None)
    priostanov = models.BooleanField(verbose_name='Приостановление операций снятия ДС со счета', null=True, default=False)
    priostanov_dop_info = models.TextField(verbose_name='Приостановление операций: Дополнительная информация/комментарии', blank=True, null=True,
                                default=None)
    SEM = models.BooleanField(verbose_name='Недружественное лицо', null=True, default=False)
    SEM_dop_info = models.TextField(verbose_name='Недружественное лицо: Дополнительная информация/комментарии', blank=True, null=True,
                                default=None)
    reorganization = models.BooleanField(verbose_name='Реорганизация / ликвидация', null=True, default=False)
    reorganization_dop_info = models.TextField(verbose_name='Реорганизация / ликвидация: Дополнительная информация/комментарии', blank=True, null=True,
                                default=None)
    unfulfilled_obligations = models.BooleanField(verbose_name='Невыполненные обязательства перед Банком', null=True, default=False)
    unfulfilled_obligations_dop_info = models.TextField(verbose_name='Невыполненные обязательства перед Банком: Дополнительная информация/комментарии', blank=True, null=True,
                                default=None)
    license_revocation = models.BooleanField(verbose_name='Отзыв лицензии', null=True, default=False)
    dop_info = models.TextField(verbose_name='Дополнительная информация/комментарии', blank=True, null=True, default=None)

    # Поля дат
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    def __str__(self):
        return f"{self.name} (ИНН: {self.inn})"

    class Meta:
        verbose_name = 'Юридическое лицо'
        verbose_name_plural = 'Юридические лица'


class ExecutiveBody(models.Model):
    """
        Модель Единоличный исполнительный орган
        Связана с Юридическим лицом
    """

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
    # необязательные поля
    job_title = models.TextField(verbose_name='Должность', blank=True, null=True, default=None)   # поле необязательное, только если ЕИО - ФЛ
    date_of_authority = models.DateField(verbose_name='Дата начала действия полномочий', blank=True, null=True, default=None)
    period_of_authority = models.TextField(verbose_name='Срок полномочий', blank=True, null=True, default=None)
    doc_of_authority = models.TextField(verbose_name='Документ, на основании которого избран ЕИО', blank=True, null=True, default=None)
    dop_info = models.TextField(verbose_name='Дополнительная информация/комментарии', blank=True, null=True, default=None)


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
    name = models.TextField(verbose_name='Имя/Наименование',  blank=True, null=True)
    inn = models.CharField(
        max_length=12,
        verbose_name='ИНН',
        validators=[
            RegexValidator(
                regex='^(\d{10}|\d{12})$',
                message='ИНН должен содержать 10 или 12 цифр',
            )
        ],
        blank=True, null=True
    )
    # Необязательные поля
    share = models.TextField(verbose_name='Доля', blank=True, null=True)
    share_info = models.TextField(verbose_name='Информация о доле', blank=True, null=True)
    address = models.TextField(verbose_name='Юрисдикция/Гражданство', blank=True, null=True, default=None)
    dop_info = models.TextField(verbose_name='Дополнительная информация/комментарии', blank=True, null=True, default=None)


    def __str__(self):
        return f"{self.name} (ИНН: {self.inn})"

    class Meta:
        verbose_name = 'Участник'
        verbose_name_plural = 'Участники'


class Collegial_governing_bodies(models.Model):
    # Модель коллегиальные органы управления
    legal_entity = models.ForeignKey(
        LegalEntity,
        on_delete=models.CASCADE,
        related_name='governing_bodies',
        verbose_name='Юридическое лицо'
    )
    bodies = (
        ('Совет директоров', 'Совет директоров'),
        ('Правление', 'Правление'),
        ('Наблюдательный совет', 'Наблюдательный совет'),
    )
    governing_bodies = models.CharField(verbose_name='Орган управления', choices=bodies, default=None, blank=True, null=True)
    period_of_authority = models.TextField(verbose_name='Срок полномочий ', blank=True, null=True)
    powers = models.TextField(verbose_name='Полномочия', blank=True, null=True)
    date_of_authority = models.DateField(verbose_name='Дата начала действия полномочий', blank=True, null=True, default=None)
    team_composition = models.TextField(verbose_name='Состав', blank=True, null=True)
    dop_info = models.TextField(verbose_name='Дополнительная информация/комментарии', blank=True, null=True,
                                default=None)

    def __str__(self):
        return self.bodies

    class Meta:
        verbose_name = 'Коллегиальный орган управления'
        verbose_name_plural = 'Коллегиальные органы управления'


class Unfriendly_countries(models.Model):
    name = models.TextField(verbose_name='Наименование')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Недружественная страна'
        verbose_name_plural = 'Недружественные страны'


class Credit_product(models.Model):
    name = models.CharField(max_length=100, verbose_name='Кредитный продукт')

    def __str__(self):
        return self.name


class Deal(models.Model):
    credit_product = models.ForeignKey(Credit_product, on_delete=models.CASCADE, related_name='participants', verbose_name='кредитный продукт', default=1)
    number = models.TextField(verbose_name='Номер')
    date = models.DateField(verbose_name='Дата')
    credit_product_type = models.TextField(verbose_name='Вид кредитного продукта')
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Сумма')
    term = models.IntegerField(verbose_name='Срок (в месяцах)')
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Процентная ставка (%)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return f"Сделка №{self.number} от {self.created_at.strftime('%d.%m.%Y')}"

    class Meta:
        verbose_name = 'Сделка'
        verbose_name_plural = 'Сделки'


class Role_in_deal(models.Model):
    name = models.CharField(max_length=100, verbose_name='Роль')

    def __str__(self):
        return self.name


class DealParticipant(models.Model):
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name='participants', verbose_name='Сделка')
    legal_entity = models.ForeignKey('LegalEntity', on_delete=models.PROTECT, related_name='deal_participations', verbose_name='Юридическое лицо')
    role = models.ForeignKey(Role_in_deal, on_delete=models.CASCADE, related_name='participants', verbose_name='роль', default=0)

    # Новые поля для крупных сделок
    is_major_deal = models.BooleanField(default=False, verbose_name='Крупная сделка')
    major_deal_criteria = models.TextField(blank=True, null=True, verbose_name='Основание для признания сделки крупной')

    def __str__(self):
        major_status = " (крупная)" if self.is_major_deal else ""
        return f"{self.legal_entity.name} - {self.get_role_display()} в сделке №{self.deal.number}{major_status}"

    class Meta:
        verbose_name = 'Участник сделки'
        verbose_name_plural = 'Участники сделки'
        unique_together = ('deal', 'legal_entity', 'role')


class Collateral(models.Model):
    """
        модель обеспечение
    """

    class CollateralType(models.TextChoices):
        REAL_ESTATE = 'RE', 'Недвижимость'
        SECURITIES = 'SE', 'Ценные бумаги'
        SHARES = 'SH', 'Доли в УК'

    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name='collaterals', verbose_name='Сделка', default=None)
    owner = models.ForeignKey(LegalEntity, on_delete=models.CASCADE, related_name='pledges',
                              verbose_name='Собственник/Залогодатель', blank=True, null=True, default=None)
    collateral_type = models.CharField(max_length=2, choices=CollateralType.choices, verbose_name='Тип обеспечения', blank=True, null=True, default=None)

    # Real Estate fields
    name = models.CharField(max_length=255, verbose_name='Наименование', null=True, blank=True)
    cadastral_number = models.CharField(max_length=255, verbose_name='Кадастровый номер', null=True, blank=True)
    address = models.TextField(verbose_name='Адрес', null=True, blank=True)
    related_objects_info = models.TextField(verbose_name='Сведения о связанных объектах', null=True, blank=True)
    registered_rights_info = models.TextField(verbose_name='Сведения о зарегестрированных правах', null=True, blank=True)
    notes = models.TextField(verbose_name='Примечания', null=True, blank=True)

    # Securities fields
    general_info_securities = models.TextField(verbose_name='Общая информация', null=True, blank=True)
    registrar = models.CharField(max_length=255, verbose_name='Держатель реестра', null=True, blank=True)

    # Shares fields
    share_size = models.CharField(max_length=255, verbose_name='Размер доли', null=True, blank=True)
    info_shares = models.TextField(verbose_name='Сведения', null=True, blank=True)

    # Common field for all types
    encumbrances = models.TextField(verbose_name='Обременения', null=True, blank=True)

    def __str__(self):
        return f'{self.get_collateral_type_display()} для сделки {self.deal.id}'

    class Meta:
        verbose_name = 'Обеспечение'
        verbose_name_plural = 'Обеспечение'