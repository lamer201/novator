from django import forms
from main.models import Material, Team
from django.contrib.auth import get_user_model

user = get_user_model()

def get_choices():
    choices = []
    for instance in Team.objects.filter(status=True):
        choices.append((instance.pk, instance.name))
    return choices

def get_shtraf_choices():
    choices = []
    for instance in Material.objects.filter(category__slug='shtrafs'):
        choices.append((instance.pk, instance.name))
    return choices


class ShtrafForm(forms.Form):
    team = forms.ChoiceField(label='Команда', choices=get_choices(), widget=forms.Select(attrs={'id': 'team-select'}))
    shtraf = forms.ChoiceField(label='Штраф', choices=get_shtraf_choices(), widget=forms.Select(attrs={'id': 'shtraf-select'}))
    category = forms.CharField(widget=forms.HiddenInput(), initial='shtrafs')