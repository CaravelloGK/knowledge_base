from django import forms
from django.forms import CheckboxSelectMultiple
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Fieldset, Row, Column, Submit, HTML, Field, Hidden
from .models import (LegalEntity, ExecutiveBody, Participant, Collateral, Risk_DealParticipant,
                     Collegial_governing_bodies, Deal, DealParticipant)
from datetime import date
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from django.core.exceptions import ValidationError


class ExecutiveBodyForm(forms.ModelForm):
    # форма для ЕИО
    class Meta:
        model = ExecutiveBody
        fields = ['name', 'inn', 'job_title',
                  'date_of_authority', 'period_of_authority','authority_is_true',
                  'doc_of_authority', 'dop_info']
        widgets = {
            'name': forms.Textarea(
                attrs={
                    'class': 'form-control readonly-field',
                    'readonly': True
                }
            ),
            'inn': forms.TextInput(attrs={'class': 'form-control readonly-field', 'readonly': True}),
            'job_title': forms.TextInput(attrs={'class': 'form-control readonly-field', 'readonly': True}),
            'date_of_authority': forms.DateInput(format='%d-%m-%Y', attrs={'type': 'date','class': 'form-control'}),
            'period_of_authority': forms.TextInput(attrs={'class': 'form-control'}),
            'authority_is_true': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'doc_of_authority': forms.TextInput(attrs={'class': 'form-control'}),
            'dop_info': forms.Textarea(
                attrs={
                    'class': 'form-control',
                }
            ),
        }
        labels = {
            'authority_is_true': 'Полномочия действительны на момент заключения',

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
            'name': forms.TextInput(attrs={'class': 'form-control readonly-field', 'readonly': True}),
            'inn': forms.TextInput(attrs={'class': 'form-control readonly-field', 'readonly': True}),
            'share': forms.TextInput(attrs={'class': 'form-control readonly-field', 'readonly': True}),
            'share_info': forms.Textarea(
                attrs={
                    'class': 'form-control readonly-field',
                    'readonly': True
                }
            ),
            'address': forms.TextInput(attrs={'class': 'form-control readonly-field', 'readonly': True}),
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
                  'powers', 'kvorum', 'date_of_authority',
                  'team_composition', 'doc_choice', 'dop_info']
        widgets = {
            'governing_bodies': forms.Select(attrs={'class': 'form-control'}),
            'period_of_authority': forms.TextInput(attrs={'class': 'form-control'}),
            'powers': forms.Textarea(
                attrs={
                    'class': 'form-control',
                }
            ),
            'kvorum': forms.Textarea(
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
            'doc_choice': forms.Textarea(
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
            'address', 'info_ustav', 'info_ustav_doc', 'info_ustav_doc_dop_info',
            'eio_uchast',
            'corp_dogovor', 'corp_dogovor_restrictions', 'corp_dogovor_conditions',
            'power', 'confirmation_procedure',
            'confirmation_procedure_dop_info',
            'sposob_vibor','kvorum',
            'zakup', 'laws_zakup', 'zakup_dop_info',
            'bankrot', 'bankrot_dop_info',
            'judicial_disputes', 'judicial_disputes_dop_info',
            'enforcement_proceedings', 'enforcement_proceedings_dop_info',
            'priostanov', 'priostanov_dop_info',
            'SEM', 'SEM_dop_info',
            'reorganization', 'reorganization_dop_info',
            'license_revocation', 'license_revocation_dop_info', 'dop_info_general'
        ]
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
            'status': forms.Textarea(attrs={'class': 'form-control',}),
            'authorized_capital': forms.TextInput(attrs={'class': 'form-control'}),
            'capital_org': forms.TextInput(attrs={'class': 'form-control readonly-field'}),
            'address': forms.TextInput(attrs={'class': 'form-control readonly-field', 'readonly': True}),
            'info_ustav': forms.Textarea(attrs={'class': 'form-control'}),
            'info_ustav_doc': forms.Textarea(attrs={'class': 'form-control'}),
            'info_ustav_doc_dop_info': forms.Textarea(attrs={'class': 'form-control'}),
            'corp_dogovor': forms.CheckboxInput(attrs={
                'class': 'form-check-input readonly-field',
                'readonly': True,
                'type': 'checkbox'}),
            'eio_uchast': forms.CheckboxInput(attrs={
                'class': 'form-check-input readonly-field',
                'readonly': True,
                'type': 'checkbox'}),
            'power': forms.Textarea(
                attrs={
                    'class': 'form-control',
                }
            ),
            'kvorum':forms.Textarea(
                attrs={
                    'class': 'form-control',
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
                'readonly': True,
                'type': 'checkbox'}),
            'laws_zakup': forms.Select(attrs={'class': 'form-control'}),
            'zakup_dop_info': forms.Textarea(
                attrs={
                    'class': 'form-control dop_info',
                }
            ),
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
                'readonly': True,
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
                'readonly': True,
                'type': 'checkbox'}),
            'SEM_dop_info': forms.Textarea(
                attrs={
                    'class': 'form-control dop_info',
                }
            ),
            'reorganization': forms.CheckboxInput(attrs={
                'class': 'form-check-input readonly-field toggle-textarea',
                'data-target': 'id_reorganization_dop_info',
                'readonly': True,
                'type': 'checkbox'}),
            'reorganization_dop_info': forms.Textarea(
                attrs={
                    'class': 'form-control dop_info',
                }
            ),
            'license_revocation': forms.CheckboxInput(attrs={
                'class': 'form-check-input readonly-field',
                'type': 'checkbox'}),
            'license_revocation_dop_info': forms.Textarea(
                attrs={
                    'class': 'form-control dop_info',
                }
            ),
            'dop_info_general': forms.Textarea(
                attrs={
                    'class': 'form-control',
                }
            ),

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Проверить корректность отображения!!!

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
            'bid_number',
            'bid_date',
            'bid_initiator',
            'bid_theme',
            'credit_product',
            'secured_obligation',
            'amount',
            'term',
            'object_of_financing',
            'financing_structure',
            'postponement',
            'waiting_period',
            'commission',
            'commission_is_law',
            'dop_info'
        ]
        widgets = {
            'credit_product': forms.Select(attrs={'class': 'form-control'}),
            'bid_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bid_date': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                }
            ),
            'bid_initiator': forms.TextInput(attrs={'class': 'form-control'}),
            'bid_theme': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 1,
                'style': 'resize:none; overflow:hidden;',
                'placeholder': 'Тема сделки'
            }),
            'secured_obligation': forms.TextInput(attrs={'class': 'form-control'}),
            'beneficiary': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.TextInput(attrs={'class': 'form-control'}),
            'term': forms.TextInput(attrs={'class': 'form-control'}),
            'object_of_financing': forms.TextInput(attrs={'class': 'form-control'}),
            'financing_structure': forms.Textarea(attrs={'class': 'form-control'}),
            'postponement': forms.TextInput(attrs={'class': 'form-control'}),
            'waiting_period': forms.TextInput(attrs={'class': 'form-control'}),
            'commission': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'commission_is_law': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'dop_info': forms.Textarea(attrs={'class': 'form-control'}),
        }


class DealParticipantForm(forms.ModelForm):
    """
        Форма для участника сделки
    """
    class Meta:
        model = DealParticipant
        fields = [
            'role',
            'kripnost',
            'is_major_deal',
            'governing_bodies',
            'major_transaction_submitted',
            'major_transaction_appropriate',
            'does_not_comply',
            'does_not_comply_corporate_agreement',
            'does_not_comply_law',
            'is_zainteres_deal',
            'zainteres_person',
            'governing_bodies_zainteres',
            'zainteres_transaction_submitted',
            'zainteres_transaction_appropriate',
            'zainteres_not_comply',
            'zainteres_not_comply_corporate_agreement',
            'zainteres_not_comply_law',
            'requires_approval',
            'the_condition_of_charter',
            'governing_bodies_other',
            'other_transaction_submitted',
            'other_transaction_appropriate',
            'other_not_comply',
            'other_not_comply_corporate_agreement',
            'other_not_comply_law',
            'zakup_1',
            'zakup_2',
            ]
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'kripnost': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 1,
                'style': 'resize:none; overflow:hidden;',
            }),
            'is_major_deal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'governing_bodies': forms.Select(attrs={'class': 'form-control'}),
            'major_transaction_submitted':forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'major_transaction_appropriate': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'does_not_comply': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'does_not_comply_corporate_agreement': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'does_not_comply_law': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_zainteres_deal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'zainteres_person': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 1,
                'style': 'resize:none; overflow:hidden;',
            }),
            'governing_bodies_zainteres': forms.Select(attrs={'class': 'form-control'}),
            'zainteres_transaction_submitted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'zainteres_transaction_appropriate': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'zainteres_not_comply': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'zainteres_not_comply_corporate_agreement': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'zainteres_not_comply_law': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'requires_approval': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'the_condition_of_charter': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 1,
                'style': 'resize:none; overflow:hidden;',
            }),
            'governing_bodies_other': forms.Select(attrs={'class': 'form-control'}),
            'other_transaction_submitted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'other_transaction_appropriate': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'other_not_comply': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'other_not_comply_corporate_agreement': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'other_not_comply_law': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'zakup_1': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'zakup_2':forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'role': 'Роль в сделке',
            'kripnost': 'Крупность',
            'is_major_deal': 'Сделка является крупной',
            'governing_bodies': 'Орган, одобряющий крупную сделку',
            'major_transaction_submitted': 'Представлено решение об одобрении крупной сделки',
            'major_transaction_appropriate': 'Решение об одобрении крупной сделки является надлежащим',
            'does_not_comply': 'Решение об одобрении крупной сделки не соответствует уставу',
            'does_not_comply_corporate_agreement': 'Решение об одобрении крупной сделки не соответствует корпоративному договору',
            'does_not_comply_law': 'Решение об одобрении крупной сделки не соответствует закону',
            'is_zainteres_deal': 'Сделка является сделкой с заинтересованностью',
            'zainteres_person': 'Заинтересованные лица и основания заинтересованности',
            'governing_bodies_zainteres': 'Орган, одобряющий крупную сделку',
            'zainteres_transaction_submitted': 'Представлено решение об одобрении сделки с заинтересованностью',
            'zainteres_transaction_appropriate': 'Решение об одобрении сделки с заинтересованностью является надлежащим',
            'zainteres_not_comply': 'Решение об одобрении сделки с заинтересованностью не соответствует уставу',
            'zainteres_not_comply_corporate_agreement': 'Решение об одобрении сделки с заинтересованностью не соответствует корпоративному договору',
            'zainteres_not_comply_law': 'Решение об одобрении сделки с заинтересованностью не соответствует закону',
            'requires_approval': 'Сделка требует одобрения в силу устава',
            'the_condition_of_charter': 'Условие устава, на основании которого требуется одобрение',
            'governing_bodies_other': 'Орган, одобряющий сделку в силу устава',
            'other_transaction_submitted': 'Представлено решение об одобрении сделки в силу устава',
            'other_transaction_appropriate': 'Решение об одобрении сделки в силу устава является надлежащим',
            'other_not_comply': 'Решение об одобрении сделки в силу устава не соответствует уставу',
            'other_not_comply_corporate_agreement': 'Решение об одобрении сделки в силу устава не соответствует корпоративному договору',
            'other_not_comply_law': 'Решение об одобрении сделки в силу устава не соответствует закону',
            'zakup_1': 'Требуются ли закупочные процедуры',
            'zakup_2': 'Закупочные процедуры соблюдены'
        }


class CollateralForm(forms.ModelForm):
    class Meta:
        model = Collateral
        fields = [
            'owner',
            'type',
             'type_of_responsibility',
            'subject_of_collateral',
            'procedure_for_foreclosure',
            'dop_info']
        widgets = {
            'owner': forms.Select(attrs={'class': 'form-select'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'type_of_responsibility': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 1,
                'style': 'resize:none; overflow:hidden;',
            }),
            'subject_of_collateral': forms.Select(attrs={'class': 'form-select'}),
            'procedure_for_foreclosure': forms.Select(attrs={'class': 'form-select'}),
            'dop_info': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 1,
                'style': 'resize:none; overflow:hidden;',
            }),
        }


class Risk_DealParticipantForm(forms.ModelForm):
    risk_type = forms.CharField(widget=forms.HiddenInput(), required=False)
    participant_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Risk_DealParticipant
        fields = [
            'risk', 'risk_faktor', 'negative_consequences',
            'minimization_measures', 'level_inherent_risk',
            'residual_risk_level', 'dop_info', 'risk_type', 'participant_id'
        ]
        widgets = {
            'risk': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'style': 'resize:none;',
            }),
            'risk_faktor': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'style': 'resize:none;',
            }),
            'negative_consequences': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'style': 'resize:none;',
            }),
            'minimization_measures': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'style': 'resize:none;',
            }),
            'level_inherent_risk': forms.Select(attrs={'class': 'form-select'}),
            'residual_risk_level': forms.Select(attrs={'class': 'form-select'}),
            'dop_info': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'style': 'resize:none;',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Hidden('risk_type', ''),
            Hidden('participant_id', ''),
            Field('risk', css_class='form-control'),
            Field('risk_faktor', css_class='form-control'),
            Field('negative_consequences', css_class='form-control d-none'),
            Field('minimization_measures', css_class='form-control'),
            Field('level_inherent_risk', css_class='form-select'),
            Field('residual_risk_level', css_class='form-select'),
            Field('dop_info', css_class='form-control'),
        )