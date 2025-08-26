from django.contrib import admin
from .models import Employee, Department

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'position', 'phone', 'manager', 'department']
    list_filter = ['position', 'department']
    search_fields = ['full_name', 'position']
    autocomplete_fields = ['manager', 'department']

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'manager', 'parent_department']
    list_filter = ['parent_department']
    search_fields = ['name']
    autocomplete_fields = ['manager', 'parent_department']