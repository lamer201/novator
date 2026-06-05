from django.contrib import admin
from .models import EcoCompensation, EcoCompensationOperation


class EcoCompensationAdmin(admin.ModelAdmin):
    list_display = ('material', 'amount', 'description')
    search_fields = ('material__name', )
    empty_value_display = '-пусто-'

class EcoCompensationOperationAdmin(admin.ModelAdmin):
    list_display = ('zakaz', 'eco_compensation', 'description')
    search_fields = ('zakaz__id', )
    list_filter = ('zakaz__team',)
    empty_value_display = '-пусто-'



admin.site.register(EcoCompensation, EcoCompensationAdmin)
admin.site.register(EcoCompensationOperation, EcoCompensationOperationAdmin)