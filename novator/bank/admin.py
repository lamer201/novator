from django.contrib import admin
from .models import Balance, Zakaz, ZakazItem, Credit, CreditPayment, Premia, HistoryOperation
from simple_history.admin import SimpleHistoryAdmin


STATUS_CHOICES = (
    ('Создан', 'Создан'),
    ('В работе', 'В работе'),
    ('Выдан', 'Выдан'),
    ('Завершен', 'Завершен'),
)

class BalanceAdmin(SimpleHistoryAdmin):
    list_display=('team', 'money', )
    history_list_display = ['money', 'history_date', 'history_user']
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

class HistoryOperationAdmin(SimpleHistoryAdmin):
    list_display = ('team', 'operation_type', 'amount', 'balance_before', 'balance_after', 'created_at')
    history_list_display = ['operation_type', 'amount', 'balance_before', 'balance_after', 'history_date', 'history_user']
    list_filter = ('operation_type', 'created_at')
    search_fields = ('team__name', 'description')


admin.site.register(Balance, BalanceAdmin)
admin.site.register(Zakaz, ZakazAdmin)
admin.site.register(ZakazItem, ZakazItemAdmin)
admin.site.register(Credit, CreditAdmin)
admin.site.register(CreditPayment, CreditPaymentAdmin)
admin.site.register(Premia, PremiaAdmin)
admin.site.register(HistoryOperation, HistoryOperationAdmin)
