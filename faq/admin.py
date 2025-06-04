from django.contrib import admin
from .models import Direction_of_business, Section, Question
from django.conf import settings
from django.shortcuts import render
from datetime import datetime


@admin.register(Direction_of_business)
class Direction_of_businessAdmin(admin.ModelAdmin):  # РУБРИКИ
    ordering = ['name']
    list_display = ('name',)
    search_fields = ['name']


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    ordering = ['name']
    list_display = ('name',)
    search_fields = ['name']


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer', 'Section', 'direction_of_business', )
    search_fields = ('question', 'answer',)
    list_filter = ('Section', 'direction_of_business', 'question')




admin.site.register(Question, QuestionAdmin)