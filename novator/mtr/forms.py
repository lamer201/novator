from django import forms
from .models import Sklad


class ShipmentForm(forms.form):
    sklad_from = forms.ChoiceField(Sklad)
    sklad_to = forms.ChoiceField(Sklad)
    