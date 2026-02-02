from django.contrib import admin
from .models import Category, Material, Team

class TeamAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'status',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class MaterialAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'price', 'category',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


admin.site.register(Team, TeamAdmin)
admin.site.register(Material, MaterialAdmin)
admin.site.register(Category, CategoryAdmin)