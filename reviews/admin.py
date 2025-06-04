from django.contrib import admin
from .models import Rubric, Category, Review
from django.conf import settings
from django.shortcuts import render

from datetime import datetime

@admin.register(Rubric)
class RubricAdmin(admin.ModelAdmin):  # РУБРИКИ
    ordering = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name',)
    search_fields = ['name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    ordering = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name',)
    search_fields = ['name']


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'name', 'description', 'link', 'category', 'powers', 'power_date',)
    filter_horizontal = ('rubric',)
    search_fields = ('name', 'title', 'description', 'current_date')
    list_filter = ('category', 'powers', 'current_date')




admin.site.register(Review, ReviewAdmin)
