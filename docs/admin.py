from django.contrib import admin
from .models import Direction_of_business, Section, Doc_class, Document, Direction, DocumentVersion, DocumentAttachment


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


class DocumentVersionInline(admin.TabularInline):
    model = DocumentVersion
    extra = 0
    readonly_fields = ('uploaded_at',)
    fields = ('version_number', 'file', 'file_type', 'version_date', 'comment', 'uploaded_by')


class DocumentAttachmentInline(admin.TabularInline):
    model = DocumentAttachment
    extra = 0
    readonly_fields = ('uploaded_at',)
    fields = ('file', 'uploaded_at', 'uploaded_by')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'global_section', 'category', 'subcategory', 'section', 'status', 'is_template', 'version_date', 'created_at')
    list_filter = ('global_section', 'category', 'subcategory', 'status', 'is_template')
    search_fields = ('title',)
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {
            'fields': ('title', 'file', 'word_file', 'status', 'is_template', 'description')
        }),
        ('Даты', {
            'fields': ('version_date',)
        }),
        ('Связи', {
            'fields': ('global_section', 'category', 'subcategory', 'section')
        }),
    )
    inlines = [DocumentVersionInline, DocumentAttachmentInline]


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ('document', 'version_number', 'file_type', 'version_date', 'uploaded_at', 'uploaded_by')
    search_fields = ('document__title',)
    list_filter = ('file_type',)
    readonly_fields = ('uploaded_at',)