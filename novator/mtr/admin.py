from django.contrib import admin
from .models import Extradition


class ExtraditionAdmin(admin.ModelAdmin):
    list_display=('material', 'team', 'year', 'month', )


admin.site.register(Extradition, ExtraditionAdmin)
