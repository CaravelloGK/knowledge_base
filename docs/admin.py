from django.contrib import admin
from .models import Direction_of_business, Section, Doc_class, Document, Direction


@admin.register(Direction_of_business)
class Direction_of_businessAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'global_section', 'description')
    list_filter = ('global_section',)
    search_fields = ('name',)


@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'global_section', 'description')
    list_filter = ('global_section',)
    search_fields = ('name',)


@admin.register(Doc_class)
class Doc_classAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    # list_filter = ('category',)
    search_fields = ('name',)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'global_section', 'category', 'subcategory', 'section', 'status', 'is_template', 'created_at')
    list_filter = ('global_section', 'category', 'subcategory', 'status', 'is_template')
    search_fields = ('title',)
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {
            'fields': ('title', 'file','status', 'is_template', 'description')
        }),
        ('Связи', {
            'fields': ('global_section', 'category', 'subcategory', 'section')
        }),
    )