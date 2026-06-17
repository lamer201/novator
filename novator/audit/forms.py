from django import forms
from main.models import Material, Team
from django.contrib.auth import get_user_model

user = get_user_model()

def get_choices():
    choices = []
    for instance in Team.objects.all():
        choices.append((instance.pk, instance.name))
    return choices

def get_shtraf_choices():
    choices = []
    for instance in Material.objects.filter(category__slug='shtrafs'):
        choices.append((instance.pk, instance.name))
    return choices

KOEFF_CHOICES = (
    (1.0, 'Без скидки'),
    (0.5, 'Скидка 50%'),
    (1.5, 'Наценка 50%'),
    (2.0, 'Наценка 100%'),
    (2.5, 'Наценка 150%'),
    (3.0, 'Наценка 200%'),
)

class ShtrafForm(forms.Form):
    team = forms.ChoiceField(label='Команда', choices=get_choices(), widget=forms.Select(attrs={'id': 'team-select'}))
    shtraf = forms.ChoiceField(label='Штраф', choices=get_shtraf_choices(), widget=forms.Select(attrs={'id': 'shtraf-select'}))
    koeff = forms.ChoiceField(label='Коэффициент', choices=KOEFF_CHOICES, required=False)
    category = forms.CharField(widget=forms.HiddenInput(), initial='shtrafs')