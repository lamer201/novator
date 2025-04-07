from django.contrib import admin
from .models import Balance, Buy, Zapusk, Zakaz


class BalanceAdmin(admin.ModelAdmin):
    list_display=('team', 'money', )
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class BuyAdmin(admin.ModelAdmin):
    list_display=('team', 'material', 'year', 'month', )
    search_fields = ('team', 'material', )
    empty_value_display = '-пусто-'


class ZapuskAdmin(admin.ModelAdmin):
    list_display=('team', 'year', 'object', )
    search_fields = ('team', )
    empty_value_display = '-пусто-'


class ZakazAdmin(admin.ModelAdmin):
    list_display=('team', 'price')
    filter_horizontal = ('material',)


admin.site.register(Balance, BalanceAdmin)
admin.site.register(Buy, BuyAdmin)
admin.site.register(Zapusk, ZapuskAdmin)
admin.site.register(Zakaz, ZakazAdmin)