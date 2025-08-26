from django import forms
from django.forms import CheckboxSelectMultiple
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Fieldset, Row, Column, Submit
from .models import LegalEntity, ExecutiveBody, Participant, Collegial_governing_bodies, Deal, DealParticipant, Collateral
from datetime import date
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from django.core.exceptions import ValidationError


class ExecutiveBodyForm(forms.ModelForm):
    # форма для ЕИО
    class Meta:
        model = ExecutiveBody
        fields = ['name', 'inn', 'job_title',
                  'date_of_authority', 'period_of_authority',
                  'doc_of_authority', 'dop_info']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control readonly-field'}),
            'inn': forms.TextInput(attrs={'class': 'form-control readonly-field'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control readonly-field'}),
            'date_of_authority': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                }
            ),
            'period_of_authority': forms.TextInput(attrs={'class': 'form-control'}),
            'doc_of_authority': forms.TextInput(attrs={'class': 'form-control'}),
            'dop_info': forms.Textarea(
                attrs={
                    'class': 'form-control',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_of_authority'].input_formats = ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y']


class ParticipantForm(forms.ModelForm):
    # форма для Участников
    class Meta:
        model = Participant
        fields = ['name', 'inn', 'share', 'share_info', 'address', 'dop_info']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control readonly-field'}),
            'inn': forms.TextInput(attrs={'class': 'form-control readonly-field'}),
            'share': forms.TextInput(attrs={'class': 'form-control readonly-field'}),
            'share_info': forms.Textarea(
                attrs={
                    'class': 'form-control readonly-field',
                    'readonly': True
                }
            ),
            'address': forms.TextInput(attrs={'class': 'form-control readonly-field'}),
            'dop_info': forms.Textarea(
                attrs={
                    'class': 'form-control',
                }
            ),
        }


class BaseCollegialBodiesFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        num_alive = sum(
            1 for f in self.forms
            if hasattr(f, "cleaned_data") and f.cleaned_data and not f.cleaned_data.get("DELETE", False)
        )
        if num_alive > 2:
            raise ValidationError(
                "У одной компании может быть не более двух коллегиальных органов управления."
            )


class Collegial_governing_bodiesForm(forms.ModelForm):
    class Meta:
        model = Collegial_governing_bodies
        fields = ['governing_bodies', 'period_of_authority',
                  'powers', 'date_of_authority',
                  'team_composition', 'dop_info']
        widgets = {
            'governing_bodies': forms.Select(attrs={'class': 'form-control'}),
            'period_of_authority': forms.TextInput(attrs={'class': 'form-control'}),
            'powers': forms.Textarea(
                attrs={
                    'class': 'form-control',
                }
            ),
            'date_of_authority': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                }
            ),
            'team_composition': forms.Textarea(
                attrs={
                    'class': 'form-control',
                }
            ),
            'dop_info': forms.Textarea(
                attrs={
                    'class': 'form-control',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_of_authority'].input_formats = ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y']


class LegalEntityForm(forms.ModelForm):
    confirmation_procedure = forms.MultipleChoiceField(
        required=False,
        label='Способ подтверждения принятия решения',
        widget=forms.CheckboxSelectMultiple,
    )

    # форма для ЮЛ
    class Meta:
        model = LegalEntity
        fields = [
            'name', 'inn', 'ogrn', 'legal_form',
            'company_group', 'status', 'authorized_capital',
            'capital_org', 'registrar', 'registrar_inn',
            'address', 'info_ustav', 'info_ustav_doc', 'eio_uchast',
            'corp_dogovor', 'monopol', 'zastroy', 'power', 'confirmation_procedure',
            'confirmation_procedure_dop_info',
            'sposob_vibor',
            'zakup', 'laws_zakup', 'zakup_win',
            'bankrot', 'bankrot_dop_info',
            'judicial_disputes', 'judicial_disputes_dop_info',
            'enforcement_proceedings', 'enforcement_proceedings_dop_info',
            'priostanov', 'priostanov_dop_info',
            'SEM', 'SEM_dop_info',
            'reorganization', 'reorganization_dop_info',
            'unfulfilled_obligations', 'unfulfilled_obligations_dop_info',
            'license_revocation', 'dop_info'
        ]
        help_texts = {
            'name': 'Наименование Юридического лица. Автоматический ввод.',
            'inn': 'ИНН Юридического лица. Автоматический ввод.',
            'ogrn': 'ОГРН Юридического лица. Автоматический ввод.',
            'legal_form': 'Организационно-правовая форма Юридического лица. Автоматический ввод.',
            'company_group': 'Группа компаний. Выберите из выпадающего списка',
            'status': 'Статус Юридического лица в ЕГРЮЛ. Автоматический ввод.',
            'authorized_capital': 'Уставной капитал Юридического лица. Автоматический ввод.',
            'capital_org': 'Доля в уставном капитале, принадлежащая Юридическому лицу.',
        }
        widgets = {
            'name': forms.Textarea(
                attrs={
                    'class': 'form-control readonly-field',
                    'readonly': True
                }
            ),
            'inn': forms.TextInput(attrs={'class': 'form-control readonly-field', 'readonly': True}),
            'ogrn': forms.TextInput(attrs={'class': 'form-control readonly-field', 'readonly': True}),
            'legal_form': forms.TextInput(attrs={'class': 'form-control readonly-field', 'readonly': True}),
            'company_group': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Textarea(
                attrs={
                    'class': 'form-control readonly-field',
                }
            ),
            'authorized_capital': forms.TextInput(attrs={'class': 'form-control readonly-field'}),
            'capital_org': forms.TextInput(attrs={'class': 'form-control readonly-field'}),
            'address': forms.TextInput(attrs={'class': 'form-control readonly-field', }),
            'info_ustav': forms.Textarea(
                attrs={
                    'class': 'form-control readonly-field',
                }
            ),
            'info_ustav_doc': forms.Textarea(
                attrs={
                    'class': 'form-control readonly-field',
                }
            ),
            'corp_dogovor': forms.CheckboxInput(attrs={
                'class': 'form-check-input readonly-field',
                'type': 'checkbox'}),
            'monopol': forms.CheckboxInput(attrs={
                'class': 'form-check-input readonly-field',
                'type': 'checkbox'}),
            'zastroy': forms.CheckboxInput(attrs={
                'class': 'form-check-input readonly-field',
                'type': 'checkbox'}),
            'eio_uchast': forms.CheckboxInput(attrs={
                'class': 'form-check-input readonly-field',
                'type': 'checkbox'}),
            'power': forms.Textarea(
                attrs={
                    'class': 'form-control readonly-field',
                }
            ),
            'confirmation_procedure_dop_info': forms.Textarea(
                attrs={
                    'class': 'form-control',
                }
            ),
            'sposob_vibor': forms.Select(attrs={'class': 'form-control'}),
            'zakup': forms.CheckboxInput(attrs={
                'class': 'form-check-input readonly-field',
                'type': 'checkbox'}),
            'laws_zakup': forms.Select(attrs={'class': 'form-control'}),
            'zakup_win': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'type': 'checkbox'}),
            'registrar': forms.TextInput(attrs={'class': 'form-control readonly-field'}),
            'registrar_inn': forms.TextInput(attrs={'class': 'form-control readonly-field'}),
            'judicial_disputes': forms.CheckboxInput(attrs={
                'class': 'form-check-input readonly-field toggle-textarea',
                'data-target': 'id_judicial_disputes_dop_info',
                'type': 'checkbox'}),
            'judicial_disputes_dop_info': forms.Textarea(
                attrs={
                    'class': 'form-control dop_info',
                }
            ),
            'bankrot': forms.CheckboxInput(attrs={
                'class': 'form-check-input readonly-field toggle-textarea',
                'data-target': 'id_bankrot_dop_info',
                'type': 'checkbox'}),
            'bankrot_dop_info': forms.Textarea(
                attrs={
                    'class': 'form-control dop_info',
                }
            ),
            'enforcement_proceedings': forms.CheckboxInput(attrs={
                'class': 'form-check-input readonly-field toggle-textarea',
                'data-target': 'id_enforcement_proceedings_dop_info',
                'type': 'checkbox'}),
            'enforcement_proceedings_dop_info': forms.Textarea(
                attrs={
                    'class': 'form-control dop_info',
                }
            ),
            'priostanov': forms.CheckboxInput(attrs={
                'class': 'form-check-input readonly-field toggle-textarea',
                'data-target': 'id_priostanov_dop_info',
                'type': 'checkbox'}),
            'priostanov_dop_info': forms.Textarea(
                attrs={
                    'class': 'form-control dop_info',
                }
            ),
            'SEM': forms.CheckboxInput(attrs={
                'class': 'form-check-input readonly-field toggle-textarea',
                'data-target': 'id_SEM_dop_info',
                'type': 'checkbox'}),
            'SEM_dop_info': forms.Textarea(
                attrs={
                    'class': 'form-control dop_info',
                }
            ),
            'reorganization': forms.CheckboxInput(attrs={
                'class': 'form-check-input readonly-field toggle-textarea',
                'data-target': 'id_reorganization_dop_info',
                'type': 'checkbox'}),
            'reorganization_dop_info': forms.Textarea(
                attrs={
                    'class': 'form-control dop_info',
                }
            ),
            'unfulfilled_obligations': forms.CheckboxInput(attrs={
                'class': 'form-check-input readonly-field toggle-textarea',
                'data-target': 'id_unfulfilled_obligations_dop_info',
                'type': 'checkbox'}),
            'unfulfilled_obligations_dop_info': forms.Textarea(
                attrs={
                    'class': 'form-control dop_info',
                }
            ),
            'license_revocation': forms.CheckboxInput(attrs={
                'class': 'form-check-input readonly-field',
                'type': 'checkbox'}),
            'dop_info': forms.Textarea(
                attrs={
                    'class': 'form-control',
                }
            ),

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Получаем текущее значение legal_form
        legal_form = None
        if self.instance and self.instance.pk:
            legal_form = self.instance.legal_form
        elif 'initial' in kwargs and 'legal_form' in kwargs['initial']:
            legal_form = kwargs['initial']['legal_form']
        # Динамически устанавливаем choices для confirmation_procedure
        if legal_form in LegalEntity.PARTS_GROUPS:
            self.fields['confirmation_procedure'].choices = LegalEntity.PARTS_GROUPS[legal_form]

    def clean_confirmation_procedure(self):
        data = self.cleaned_data.get('confirmation_procedure', [])
        # Убедимся, что это список строк (value)
        if not isinstance(data, list):
            data = list(data)
        return data


class DealForm(forms.ModelForm):
    """
        Форма для сделки
    """


    class Meta:
        model = Deal
        fields = [
            'number', 'date', 'credit_product', 'amount', 'term',
            'interest_rate',
        ]
        widgets = {
            'credit_product': forms.Select(attrs={'class': 'form-control'}),
            'number': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                }
            ),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'term': forms.NumberInput(attrs={'class': 'form-control'}),
            'interest_rate': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class DealParticipantForm(forms.ModelForm):
    """
        Форма для участника сделки
    """
    class Meta:
        model = DealParticipant
        fields = ['role', 'is_major_deal', 'major_deal_criteria']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'is_major_deal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'major_deal_criteria': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'role': 'Роль в сделке',
            'is_major_deal': 'Является ли сделка крупной для этого участника?',
            'major_deal_criteria': 'Основание для признания сделки крупной (если применимо)',
        }


class CollateralForm(forms.ModelForm):
    """
        Форма для обеспечения
    """
    class Meta:
        model = Collateral
        fields = '__all__'
        exclude = ('deal',)  # deal будет установлен во view
        widgets = {
            'address': forms.Textarea(
                attrs={
                    'class': 'form-control',
                }
            ),
            'related_objects_info': forms.Textarea(
                attrs={
                    'class': 'form-control',
                }
            ),
            'registered_rights_info': forms.Textarea(
                attrs={
                    'class': 'form-control',
                }
            ),
            'general_info_securities': forms.Textarea(
                attrs={
                    'class': 'form-control',
                }
            ),
            'registrar': forms.TextInput(attrs={'class': 'form-control'}),
            'share_size': forms.TextInput(attrs={'class': 'form-control'}),
            'info_shares': forms.Textarea(
                attrs={
                    'class': 'form-control',
                }
            ),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Row(
                Column('owner', css_class='form-group col-md-6 mb-0'),
                Column('collateral_type', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Div(
                Fieldset(
                    'Данные по недвижимости',
                    'name',
                    'cadastral_number',
                    'address',
                    'related_objects_info',
                    'registered_rights_info',
                    'notes',
                    'encumbrances'
                ),
                css_class='real-estate-fields'
            ),
            Div(
                Fieldset(
                    'Данные по ценным бумагам',
                    'general_info_securities',
                    'registrar',
                    'encumbrances'
                ),
                css_class='securities-fields'
            ),
            Div(
                Fieldset(
                    'Данные по долям в УК',
                    'share_size',
                    'info_shares',
                    'encumbrances'
                ),
                css_class='shares-fields'
            ),
        )