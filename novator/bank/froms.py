from .models import Zakaz
from django import forms

class ZakazForm(forms.ModelForm):
    class Meta:
        model = Zakaz
        fields = (
            'team',
            'material',
            'price'
        )
        filter_horizontal = ('material',)
   