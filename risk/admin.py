from django.contrib import admin
from django.contrib import admin
from .models import Direction, Kind, Subject, Risk
from django.conf import settings
from django.shortcuts import render
from datetime import datetime


@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):  # РУБРИКИ
    ordering = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name',)
    search_fields = ['name']


@admin.register(Kind)
class CategoryAdmin(admin.ModelAdmin):
    ordering = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name',)
    search_fields = ['name']


@admin.register(Subject)
class CategoryAdmin(admin.ModelAdmin):
    ordering = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name',)
    search_fields = ['name']


class RiskAdmin(admin.ModelAdmin):
    list_display = ('direction', 'kind', 'subject', 'risk', 'risk_factor',
                    'legal_basis', 'negative_consequences',
                    'minimization_measures', 'associated_risks', 'info_about_risk_realization')
    search_fields = ('direction', 'kind', 'subject', 'risk')




admin.site.register(Risk, RiskAdmin)

