from django.contrib import admin
from .models import LegalEntity, ExecutiveBody, Participant, Collegial_governing_bodies, DealParticipant, Collateral, Deal, Credit_product, Role_in_deal


# Используем TabularInline для удобного редактирования связанных объектов
class DealParticipantInline(admin.TabularInline):
    model = DealParticipant
    extra = 1  # Количество пустых форм для добавления


class CollateralInline(admin.TabularInline):
    model = Collateral
    extra = 1


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
# модель участники
class CollegialAdmin(admin.ModelAdmin):
    list_display = ['governing_bodies', 'legal_entity', ]
    list_filter = ['legal_entity']


@admin.register(Role_in_deal)
# модель участники
class Role_in_dealAdmin(admin.ModelAdmin):
    list_display = ['name', ]
    list_filter = ['name']


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ('number', 'date', 'credit_product', 'amount',)
    list_filter = ('credit_product', 'created_at')
    inlines = [DealParticipantInline, CollateralInline]  # Добавляем инлайны на страницу сделки
    readonly_fields = ('created_at',)


@admin.register(Credit_product)
# модель участники
class Credit_productAdmin(admin.ModelAdmin):
    list_display = ['name', ]
    list_filter = ['name']


@admin.register(DealParticipant)
class DealParticipantAdmin(admin.ModelAdmin):
    list_display = ('deal', 'legal_entity', 'role', 'is_major_deal')
    list_filter = ('role', 'is_major_deal')


@admin.register(Collateral)
class CollateralAdmin(admin.ModelAdmin):
    list_display = ('id', 'deal', 'owner', 'get_collateral_type_display', 'name', 'cadastral_number')
    list_filter = ('collateral_type', 'deal', 'owner')
    search_fields = ('name', 'cadastral_number', 'address', 'deal__id')
    fieldsets = (
        ('Основная информация', {
            'fields': ('deal', 'owner', 'collateral_type')
        }),
        ('Недвижимость', {
            'fields': ('name', 'cadastral_number', 'address', 'related_objects_info', 'registered_rights_info', 'notes'),
            'classes': ('collapse',),
        }),
        ('Ценные бумаги', {
            'fields': ('general_info_securities', 'registrar'),
            'classes': ('collapse',),
        }),
        ('Доли в УК', {
            'fields': ('share_size', 'info_shares'),
            'classes': ('collapse',),
        }),
        ('Общее', {
            'fields': ('encumbrances',),
        }),
    )

    def get_collateral_type_display(self, obj):
        return obj.get_collateral_type_display()
    get_collateral_type_display.short_description = 'Тип обеспечения'