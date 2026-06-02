from bank.models import Zakaz, Team, ZakazItem, Material
from django import forms
from django.contrib.auth import get_user_model

class ZakazFormPremii(forms.Form):
    material = forms.ChoiceField(label='Материал', choices=[(material.pk, material.name) for material in Material.objects.filter(category__slug='premii')], widget=forms.Select(attrs={'id': 'material-select'}))
    category = forms.CharField(widget=forms.HiddenInput(), initial='premii')