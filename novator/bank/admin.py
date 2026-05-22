from django.contrib import admin
from .models import Balance, Zakaz, ZakazItem, Credit, CreditPayment, Premia, Consumers


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


class ZakazAdmin(admin.ModelAdmin):
    list_display=('id','team', 'year', 'month', 'payment', 'status', 'description')
    search_fields = ('team', 'status', 'description')
    
class CreditAdmin(admin.ModelAdmin):
    list_display=('team', 'amount', 'year', 'percent', 'remains', 'status')
    search_fields = ('team', )
    empty_value_display = '-пусто-'

class CreditPaymentAdmin(admin.ModelAdmin):
    list_display=('credit', 'amount', 'year', )
    search_fields = ('team', )
    empty_value_display = '-пусто-'


class ZakazItemAdmin(admin.ModelAdmin):
   list_display = ('zakaz','material', 'price', 'quantity', 'koeff', 'refund')

class PremiaAdmin(admin.ModelAdmin):
    list_display = ('team', 'amount', 'year')
    search_fields = ('team', )
    empty_value_display = '-пусто-'

class ConsumersAdmin(admin.ModelAdmin):
    list_display = ('name', 'profit_val')
    search_fields = ('name', )
    empty_value_display = '-пусто-'


admin.site.register(Balance, BalanceAdmin)
admin.site.register(Zakaz, ZakazAdmin)
admin.site.register(ZakazItem, ZakazItemAdmin)
admin.site.register(Credit, CreditAdmin)
admin.site.register(CreditPayment, CreditPaymentAdmin)
admin.site.register(Premia, PremiaAdmin)
admin.site.register(Consumers, ConsumersAdmin)