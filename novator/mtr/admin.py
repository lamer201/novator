from django.contrib import admin
from .models import Extradition, Sklad, Material, Stock, Shipment


class ExtraditionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'team', 'material', 'year', 'month')
    search_fields = ('team__name', 'material__material__name')
    empty_value_display = '-пусто-'


class SkladAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('name__name',)
    empty_value_display = '-пусто-'


class MaterialAdmin(admin.ModelAdmin):
    list_display = ('pk', 'material', 'sklad')
    search_fields = ('material__material__name',)
    empty_value_display = '-пусто-'


class StockAdmin(admin.ModelAdmin):
    list_display = ('pk', 'warehouse', 'material', 'quantity')
    search_fields = ('warehouse__name', 'material__material__name')
    empty_value_display = '-пусто-'


class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'date_time', 'from_warehouse', 'to_warehouse')
    search_fields = ('from_warehouse__name', 'to_warehouse__name')
    empty_value_display = '-пусто-'

admin.site.register(Extradition, ExtraditionAdmin)
admin.site.register(Sklad, SkladAdmin)
admin.site.register(Material, MaterialAdmin)
admin.site.register(Stock, StockAdmin)
admin.site.register(Shipment, ShipmentAdmin)