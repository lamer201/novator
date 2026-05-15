from django.contrib import admin
from .models import Balance, Buy, Zapusk, Zakaz, ZakazItem, Credit, CreditPayment


STATUS_CHOICES = (
    ('Создан', 'Создан'),
    ('В работе', 'В работе'),
    ('Выдан', 'Выдан'),
    ('Завершен', 'Завершен'),
)

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
    list_display=('id','team', 'year', 'month', 'payment', 'status', 'description')
    search_fields = ('team', 'status', 'description')
    
class CreditAdmin(admin.ModelAdmin):
    list_display=('team', 'amount', 'year', 'percent', 'total_price', 'remains', 'remains_percent')
    readonly_fields = ('total_price',)
    search_fields = ('team', )
    empty_value_display = '-пусто-'

class CreditPaymentAdmin(admin.ModelAdmin):
    list_display=('credit', 'amount', 'year', )
    search_fields = ('team', )
    empty_value_display = '-пусто-'


class ZakazItemAdmin(admin.ModelAdmin):
   list_display = ('zakaz','material', 'price', 'quantity', 'koeff', 'refund')


admin.site.register(Balance, BalanceAdmin)
admin.site.register(Buy, BuyAdmin)
admin.site.register(Zapusk, ZapuskAdmin)
admin.site.register(Zakaz, ZakazAdmin)
admin.site.register(ZakazItem, ZakazItemAdmin)
admin.site.register(Credit, CreditAdmin)
admin.site.register(CreditPayment, CreditPaymentAdmin)