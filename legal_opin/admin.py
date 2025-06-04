from django.contrib import admin
from .models import LegalEntity, ExecutiveBody, Participant, Deal

@admin.register(LegalEntity)
class LegalEntityAdmin(admin.ModelAdmin):
    list_display = ['name', 'inn', 'ogrn', 'legal_form', 'company_group', 'status', 'created_at', 'updated_at']
    search_fields = ['name', 'inn', 'ogrn']
    list_filter = ['legal_form', 'company_group', 'status']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ExecutiveBody)
class ExecutiveBodyAdmin(admin.ModelAdmin):
    list_display = ['name', 'inn', 'legal_entity']
    search_fields = ['name', 'inn']
    list_filter = ['legal_entity']

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['name', 'inn', 'legal_entity', 'share']
    search_fields = ['name', 'inn']
    list_filter = ['legal_entity']

@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ['number', 'date', 'credit_product_type']
    search_fields = ['number', 'credit_product_type']
    list_filter = ['date', 'credit_product_type']
    filter_horizontal = ['legal_entities']