from django.contrib import admin
from .models import EcoCompensation, EcoCompensationOperation, HistoryOperation


class EcoCompensationAdmin(admin.ModelAdmin):
    list_display = ('material', 'amount', 'description')
    search_fields = ('material__name', )
    empty_value_display = '-пусто-'

class EcoCompensationOperationAdmin(admin.ModelAdmin):
    list_display = ('zakaz', 'eco_compensation', 'operation_type', 'created_at', 'description')
    search_fields = ('zakaz__id', 'description')
    list_filter = ('operation_type', 'zakaz__team',)
    empty_value_display = '-пусто-'

class HistoryOperationAdmin(admin.ModelAdmin):
    list_display = ('zakaz', 'team', 'operation_type', 'description')
    search_fields = ('zakaz__id', 'team__name', 'description')
    list_filter = ('operation_type', 'team',)
    empty_value_display = '-пусто-'


admin.site.register(EcoCompensation, EcoCompensationAdmin)
admin.site.register(EcoCompensationOperation, EcoCompensationOperationAdmin)
admin.site.register(HistoryOperation, HistoryOperationAdmin)