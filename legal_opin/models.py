from django.db import models
from django.core.validators import RegexValidator
from django.contrib.postgres.fields import ArrayField
from django.db.models import CASCADE


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
    authorized_capital = models.TextField(verbose_name='Уставной капитал', blank=True, null=True)
    capital_org = models.TextField(verbose_name='Информация о доле в уставном капитале, принадлежащей обществу', blank=True, null=True)

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
    address = models.TextField(verbose_name='Местонахождение', default=None)
    info_ustav = models.TextField(verbose_name='Информация о действующей редакции устава', blank=True, null=True, default=None)
    info_ustav_doc = models.TextField(verbose_name='Последние изменения в учредительные документы', blank=True, null=True, default=None)
    info_ustav_doc_dop_info = models.TextField(verbose_name='Учредительные документы: Дополнительная информация/комментарии',
                                                       blank=True, null=True, default=None)
    eio_uchast = models.BooleanField(verbose_name='ЕИО – единственный участник/акционер ЮЛ', null=True, default=None)
    corp_dogovor = models.BooleanField(verbose_name='Корпоративный договор', null=True, default=None)
    corp_dogovor_restrictions = models.TextField(verbose_name='Ограничения, выявленые в корпоративном договоре',
                                                       blank=True, null=True, default=None)
    corp_dogovor_conditions = models.TextField(verbose_name='Условия порядка распределения голосов по корпоративному договору',
                                                       blank=True, null=True, default=None)
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
        'ОАО': [
            ('Подписания лицом, осуществляющим ведение реестра акционеров и выполняющим функции счетной комиссии',
             'Подписания лицом, осуществляющим ведение реестра акционеров и выполняющим функции счетной комиссии'),
            (
            'Нотариального подтверждения / удостоверения лицом, осуществляющим ведение реестра акционеров и выполняющим функции счетной комиссии',
            'Нотариального подтверждения / удостоверения лицом, осуществляющим ведение реестра акционеров и выполняющим функции счетной комиссии'),
        ],
        'ЗАО': [
            ('Подписания лицом, осуществляющим ведение реестра акционеров и выполняющим функции счетной комиссии',
             'Подписания лицом, осуществляющим ведение реестра акционеров и выполняющим функции счетной комиссии'),
            ('Нотариального подтверждения / удостоверения лицом, осуществляющим ведение реестра акционеров и выполняющим функции счетной комиссии', 'Нотариального подтверждения / удостоверения лицом, осуществляющим ведение реестра акционеров и выполняющим функции счетной комиссии'),
        ],
        'ПАО': [
            ('подтверждается лицом, осуществляющим ведение реестра акционеров такого общества и выполняющим функции счетной комиссии',
             'подтверждается лицом, осуществляющим ведение реестра акционеров такого общества и выполняющим функции счетной комиссии'),
        ],
    }
    confirmation_procedure = ArrayField(models.CharField(), blank=True, null=True, default=list, verbose_name='Принятое решение ОСУ/ ОСА подтверждается путем')
    confirmation_procedure_dop_info = models.TextField(verbose_name='Дополнительная информация/комментарии',
                                                       blank=True, null=True, default=None)

    sposob = (
        ('Устав', 'Устав'),
        ('Решение', 'Решение'),
        ('Закон', 'Закон'),
    )
    sposob_vibor = models.CharField(verbose_name='Указанный способ закреплен в документе', choices=sposob, default=None, blank=True, null=True)
    kvorum = models.TextField(verbose_name='Кворум и необходимое кол-во голосов для принятия решений', blank=True, null=True,
                                  default=None)
    zakup = models.BooleanField(verbose_name='Заказчик по закупкам', null=True, default=None)
    laws = (
        ('44-ФЗ', '44-ФЗ'),
        ('223-ФЗ', '223-ФЗ'),
        ('44-ФЗ и 223-ФЗ', '44-ФЗ и 223-ФЗ'),
    )
    laws_zakup = models.CharField(verbose_name='Закон по закупкам', choices=laws, default=None, blank=True, null=True)
    zakup_dop_info = models.BooleanField(verbose_name='Закон по закупкам: Дополнительная информация/комментарии', blank=True, null=True,
                                default=None)
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
    license_revocation_dop_info = models.TextField(verbose_name='Отзыв лицензии: Дополнительная информация/комментарии', blank=True, null=True,
                                default=None)
    dop_info_general = models.TextField(verbose_name='Дополнительная информация/комментарии', blank=True, null=True, default=None)

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
    name = models.TextField(verbose_name='Ф.И.О./Наименование')
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
    authority_is_true = models.BooleanField(default=False, verbose_name='Полномочия действительны на момент составления юридического заключения', blank=True, null=True)
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
    share_info = models.TextField(verbose_name='Информация об ограничениях/обременениях в отношении доли', blank=True, null=True)
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
    kvorum = models.TextField(verbose_name='Кворум и кол-во голосов для принятия решений', blank=True, null=True, default=None)
    date_of_authority = models.DateField(verbose_name='Дата начала действия полномочий', blank=True, null=True, default=None)
    team_composition = models.TextField(verbose_name='Состав', blank=True, null=True)
    doc_choice = models.TextField(verbose_name='Документ, на основании которого избран ОУ', blank=True, null=True,
                              default=None)
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
    # модель список кредитных продуктов
    name = models.CharField(max_length=100, verbose_name='Кредитный продукт')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Вид кредитного продукта'
        verbose_name_plural = 'Виды кредитного продукта'


class Deal(models.Model):
    # модель сделка (параметры кредитного продукта)
    bid_number = models.TextField(verbose_name='Номер')
    bid_date = models.DateField(verbose_name='Дата', null=True, blank=True)
    bid_initiator = models.TextField(verbose_name='Инициатор')
    bid_theme = models.TextField(verbose_name='Тема')
    credit_product = models.ForeignKey(Credit_product, on_delete=models.CASCADE, related_name='participants', verbose_name='кредитный продукт', default=1)
    secured_obligation = models.TextField(verbose_name='Обеспечиваемое обязательство', blank=True, null=True, default=None)
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Сумма')

    term = models.TextField(verbose_name='Срок', blank=True, null=True, default=None)
    object_of_financing = models.TextField(verbose_name='Объект финансирования', blank=True, null=True, default=None)
    financing_structure = models.TextField(verbose_name='Структура финансирования', blank=True, null=True, default=None)
    postponement = models.TextField(verbose_name='Отсрочка', blank=True, null=True, default=None)
    waiting_period = models.TextField(verbose_name='Период ожидания', blank=True, null=True, default=None)
    beneficiary = models.TextField(verbose_name='бенифициар', blank=True, null=True, default=None)
    commission = models.BooleanField(default=False, verbose_name='Предусмотрена комиссия', blank=True, null=True)
    commission_is_law = models.BooleanField(default=False, verbose_name='комиссия соответствует закону', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    dop_info = models.TextField(verbose_name='Дополнительная информация/комментарии', blank=True, null=True,
                                default=None)

    def __str__(self):
        return f"Сделка №{self.bid_number} от {self.created_at.strftime('%d.%m.%Y')}"

    class Meta:
        verbose_name = 'Сделка'
        verbose_name_plural = 'Сделки'


class Role_in_deal(models.Model):
    # модель роль - список ролей в сделке
    name = models.CharField(max_length=100, verbose_name='Роль')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'


class DealParticipant(models.Model):
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name='participants', verbose_name='Сделка')
    legal_entity = models.ForeignKey('LegalEntity', on_delete=models.PROTECT, related_name='deal_participations', verbose_name='Юридическое лицо')
    role = models.ForeignKey(Role_in_deal, on_delete=models.CASCADE, related_name='participants', verbose_name='роль', default="")

    bodies_1 = (
        ('', 'Выберите из списка'),
        ('Совет директоров', 'Совет директоров'),
        ('ОСУ/ОСА', 'ОСУ/ОСА'),
        ('Единственный участник/акционер', 'Единственный участник/акционер'),
    )

    # поля для участника сделки
    # крупная сделка
    kripnost = models.TextField(verbose_name='Крупность', blank=True, null=True)
    is_major_deal = models.BooleanField(default=False, verbose_name='Сделка является крупной')
    governing_bodies = models.CharField(verbose_name='Орган, одобряющий крупную сделку', choices=bodies_1, default='', blank=True, null=True)
    major_transaction_submitted = models.BooleanField(default=False, verbose_name='Представлено решение об одобрении крупной сделки')
    major_transaction_appropriate = models.BooleanField(default=False, verbose_name='Решение об одобрении крупной сделки является надлежащим')
    does_not_comply = models.BooleanField(default=False, verbose_name='Решение об одобрении крупной сделки не соответствует уставу')
    does_not_comply_corporate_agreement = models.BooleanField(default=False, verbose_name='Решение об одобрении крупной сделки не соответствует корпоративному договору')
    does_not_comply_law = models.BooleanField(default=False, verbose_name='Решение об одобрении крупной сделки не соответствует закону')
    # сделка с заинтересованностью
    is_zainteres_deal = models.BooleanField(default=False, verbose_name='Сделка является сделкой с заинтересованностью')
    zainteres_person = models.TextField(verbose_name='Заинтересованные лица и основания заинтересованности', blank=True, null=True)
    governing_bodies_zainteres = models.CharField(verbose_name='Орган, одобряющий крупную сделку', choices=bodies_1, default='', blank=True)
    zainteres_transaction_submitted = models.BooleanField(default=False, verbose_name='Представлено решение об одобрении сделки с заинтересованностью')
    zainteres_transaction_appropriate = models.BooleanField(default=False, verbose_name='Решение об одобрении сделки с заинтересованностью является надлежащим')
    zainteres_not_comply = models.BooleanField(default=False, verbose_name='Решение об одобрении сделки с заинтересованностью не соответствует уставу')
    zainteres_not_comply_corporate_agreement = models.BooleanField(default=False, verbose_name='Решение об одобрении сделки с заинтересованностью не соответствует корпоративному договору')
    zainteres_not_comply_law = models.BooleanField(default=False, verbose_name='Решение об одобрении сделки с заинтересованностью не соответствует закону')
    # иное
    requires_approval = models.BooleanField(default=False, verbose_name='Сделка требует одобрения в силу устава')
    the_condition_of_charter = models.TextField(verbose_name='Условие устава, на основании которого требуется одобрение ', blank=True,
                                        null=True)
    governing_bodies_other = models.CharField(verbose_name='Орган, одобряющий сделку в силу устава', choices=bodies_1, default='', blank=True,
                                        null=True)
    other_transaction_submitted = models.BooleanField(default=False, verbose_name='Представлено решение об одобрении сделки в силу устава')
    other_transaction_appropriate = models.BooleanField(default=False, verbose_name='Решение об одобрении сделки в силу устава является надлежащим')
    other_not_comply = models.BooleanField(default=False, verbose_name='Решение об одобрении сделки в силу устава не соответствует уставу')
    other_not_comply_corporate_agreement = models.BooleanField(default=False, verbose_name='Решение об одобрении сделки в силу устава не соответствует корпоративному договору')
    other_not_comply_law = models.BooleanField(default=False, verbose_name='Решение об одобрении сделки в силу устава не соответствует закону')
    zakup_1 = models.BooleanField(default=False, verbose_name='Требуются ли закупочные процедуры')
    zakup_2 = models.BooleanField(default=False, verbose_name='Закупочные процедуры соблюдены')


    def __str__(self):
        return f"{self.legal_entity.name} в сделке №{self.deal.bid_number}"

    class Meta:
        verbose_name = 'Участник сделки'
        verbose_name_plural = 'Участники сделки'
        unique_together = ('deal', 'legal_entity', 'role')


class Type_Collateral(models.Model):
    # модель список предметов залога
    name = models.CharField(max_length=100, verbose_name='Предмет залога')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тип обеспечения'
        verbose_name_plural = 'Типы обеспечения'


class Collateral(models.Model):

    type_collateral = (
         ('', 'Выберите из списка'),
         ('Поручительство', 'Поручительство'),
         ('Залог', 'Залог'),
         ('Гарантия', 'Гарантия'),
         )

    order = (
         ('', 'Выберите из списка'),
         ('судебный', 'судебный'),
         ('внесудебный', 'внесудебный'),
         )

    deal = models.ForeignKey(Deal, on_delete=CASCADE, related_name='Collateral', verbose_name='Сделка', blank=True, null=True)
    owner = models.ForeignKey('LegalEntity', on_delete=CASCADE, related_name='owners', verbose_name='Наименование контрагента', blank=True, null=True)
    type = models.CharField(verbose_name='Вид обеспечения', choices=type_collateral, default='', blank=True, null=True, )
    type_of_responsibility = models.TextField(verbose_name='Вид ответственности', blank=True, null=True, default='')
    subject_of_collateral = models.ForeignKey('Type_Collateral',
                                               on_delete=CASCADE,
                                               related_name='types',
                                               verbose_name='Предмет залога',
                                               default='',
                                                blank=True, null=True
                                               )
    procedure_for_foreclosure = models.CharField(verbose_name='Порядок обращения взыскания', choices=order, default='', blank=True, null=True)
    dop_info = models.TextField(verbose_name='Дополнительная информация/комментарии', blank=True, null=True,
                                 default=None)

    class Meta:
         verbose_name = "Обеспечение"
         verbose_name_plural = "Обеспечения"

    def __str__(self):
         return f"{self.owner} - {self.type}"


class Risk_Ul(models.Model):

    level = (
         ('', 'Выберите из списка'),
         ('Низкий', 'Низкий'),
         ('Средний', 'Средний'),
         ('Высокий', 'Высокий'),
         )
    risk = models.TextField(verbose_name='риск', blank=True, null=True, default='')
    risk_faktor = models.TextField(verbose_name='риск-фактор', default='', blank=True, null=True)
    negative_consequences = models.TextField(verbose_name='негативные последствия', blank=True, null=True, default='')
    minimization_measures = models.TextField(verbose_name='меры минимизации', blank=True, null=True, default='')
    level_inherent_risk = models.CharField(verbose_name='уровень присущего риска', choices=level, default='',
                                                 blank=True, null=True)
    residual_risk_level = models.CharField(verbose_name='уровень остаточного риска', choices=level, default='',
                                                 blank=True, null=True)
    dop_info = models.TextField(verbose_name='Дополнительная информация/комментарии', blank=True, null=True,
                                 default=None)

    class Meta:
         verbose_name = "Риск ЮЛ"
         verbose_name_plural = "Риски ЮЛ"


class Risk_DealParticipant(models.Model):

    level = (
         ('', 'Выберите из списка'),
         ('Низкий', 'Низкий'),
         ('Средний', 'Средний'),
         ('Высокий', 'Высокий'),
         )
    risk = models.TextField(verbose_name='риск', blank=True, null=True, default='')
    risk_faktor = models.TextField(verbose_name='риск-фактор', default='', blank=True, null=True)
    negative_consequences = models.TextField(verbose_name='негативные последствия', blank=True, null=True, default='')
    minimization_measures = models.TextField(verbose_name='меры минимизации', blank=True, null=True, default='')
    level_inherent_risk = models.CharField(verbose_name='уровень присущего риска', choices=level, default='',
                                                 blank=True, null=True)
    residual_risk_level = models.CharField(verbose_name='уровень остаточного риска', choices=level, default='',
                                                 blank=True, null=True)
    dop_info = models.TextField(verbose_name='Дополнительная информация/комментарии', blank=True, null=True,
                                 default=None)
    deal = models.ForeignKey(Deal, on_delete=CASCADE, related_name='risk_deal', verbose_name='Сделка', blank=True, null=True)
    owner = models.ForeignKey('LegalEntity', on_delete=CASCADE, related_name='risk_owner_owners', verbose_name='Наименование контрагента', blank=True, null=True)


    class Meta:
        verbose_name = "Риск участика сделки"
        verbose_name_plural = "Риски участников сделки"


class Risk_help(models.Model):
    field_ul = models.CharField(verbose_name='Поле', default='', blank=True, null=True, )
    identefik = models.CharField(verbose_name='Идентификатор', default='', blank=True, null=True, )
    value_field_ul = models.CharField(verbose_name='Занчение идентификатора', default='', blank=True, null=True, )

    class Meta:
         verbose_name = "значение поля"
         verbose_name_plural = "значения полей"

    def __str__(self):
        return self.field_ul