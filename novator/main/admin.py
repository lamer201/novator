from django.contrib import admin
from .models import Category, ItemProperty, Material, Team, Status

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

class StatusAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name')
    search_fields = ('name',)
    empty_value_display = '-пусто-'

class ItemPropertyAdmin(admin.ModelAdmin):
    list_display = ('pk', 'material', 'property_name', 'property_value')
    search_fields = ('material__name', 'property_name', 'property_value')
    empty_value_display = '-пусто-'

admin.site.register(Team, TeamAdmin)
admin.site.register(Material, MaterialAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Status, StatusAdmin)
admin.site.register(ItemProperty, ItemPropertyAdmin)
