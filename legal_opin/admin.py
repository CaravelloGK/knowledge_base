from django.contrib import admin
from .models import (LegalEntity, ExecutiveBody, Risk_DealParticipant, Participant, Collegial_governing_bodies,
                     DealParticipant, Deal, Credit_product, Role_in_deal, Type_Collateral, Collateral, Risk_help)


# Используем TabularInline для удобного редактирования связанных объектов
class DealParticipantInline(admin.TabularInline):
    model = DealParticipant
    extra = 1  # Количество пустых форм для добавления


@admin.register(LegalEntity)
# модель ЮЛ
class LegalEntityAdmin(admin.ModelAdmin):
    list_display = ['name', 'inn', 'ogrn', 'legal_form', 'company_group', 'status', 'created_at', 'updated_at']
    search_fields = ['name', 'inn', 'ogrn']
    list_filter = ['legal_form', 'company_group', 'status']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ExecutiveBody)
# модель ЕИО
class ExecutiveBodyAdmin(admin.ModelAdmin):
    list_display = ['name', 'inn', 'legal_entity']
    search_fields = ['name', 'inn']
    list_filter = ['legal_entity']


@admin.register(Participant)
# модель участники
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['name', 'inn', 'legal_entity', 'share']
    search_fields = ['name', 'inn']
    list_filter = ['legal_entity']


@admin.register(Collegial_governing_bodies)
# модель коллегиальные органы
class CollegialAdmin(admin.ModelAdmin):
    list_display = ['governing_bodies', 'legal_entity', ]
    list_filter = ['legal_entity']


@admin.register(Role_in_deal)
# модель участник сделки (список ролей)
class Role_in_dealAdmin(admin.ModelAdmin):
    list_display = ['name', ]
    list_filter = ['name']


@admin.register(Deal)
# модель сделка
class DealAdmin(admin.ModelAdmin):
    list_display = ('bid_number', 'bid_date', 'credit_product', 'amount',)
    list_filter = ('credit_product', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Credit_product)
# модель тип кредитного продукта
class Credit_productAdmin(admin.ModelAdmin):
    list_display = ['name', ]
    list_filter = ['name']


@admin.register(DealParticipant)
# модель участники сделки
class DealParticipantAdmin(admin.ModelAdmin):
    list_display = ('deal', 'legal_entity', 'role')
    list_filter = ('deal','role')


@admin.register(Type_Collateral)
# модель тип обеспечения
class Type_CollateralAdmin(admin.ModelAdmin):
    list_display = ['name', ]
    list_filter = ['name']


@admin.register(Collateral)
class CollateralAdmin(admin.ModelAdmin):
    list_display = ('deal', 'owner', 'type')
    list_filter = ('deal', 'owner')


@admin.register(Risk_DealParticipant)
class Risk_DealParticipantlAdmin(admin.ModelAdmin):
    list_display = ('risk', 'owner', 'deal')
    list_filter = ('deal', 'owner')


@admin.register(Risk_help)
class Risk_helpAdmin(admin.ModelAdmin):
    list_display = ('field_ul',)
    list_filter = ('identefik', 'value_field_ul')