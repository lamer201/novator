from django.contrib import admin
from .models import Category, ItemProperty, Material, Team, Status, Koeff, UserProfile, EcoScore, EcoScoreOperation

class TeamAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'status',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class MaterialAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'price', 'category', 'slug', 'eco_score')
    search_fields = ('name',)
    list_filter = ["category",]
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

class KoeffAdmin(admin.ModelAdmin):
    list_display = ('pk', 'material', 'koeff_value')
    search_fields = ('material__name',)
    empty_value_display = '-пусто-'


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'role', 'sklad')
    search_fields = ('user__username', 'role')
    empty_value_display = '-пусто-'


class EcoScoreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'team', 'score')
    search_fields = ('team__name',)
    empty_value_display = '-пусто-'

class EcoScoreOperationAdmin(admin.ModelAdmin):
    list_display = ('pk', 'eco_score', 'operation', 'item', 'year')
    empty_value_display = '-пусто-'


admin.site.register(Team, TeamAdmin)
admin.site.register(Material, MaterialAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Status, StatusAdmin)
admin.site.register(Koeff, KoeffAdmin)
admin.site.register(ItemProperty, ItemPropertyAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(EcoScore, EcoScoreAdmin)
admin.site.register(EcoScoreOperation, EcoScoreOperationAdmin)