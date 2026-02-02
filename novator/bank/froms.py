from .models import Zakaz, Team
from django import forms

def get_choices():
    choices = []
    for instance in Team.objects.filter(status=True):
        choices.append((instance.pk, instance.name))
    return choices


class ZakazForm1(forms.Form):
    team = forms.ChoiceField(label='Команда', choices=get_choices())
    TDU500 = forms.IntegerField(label='Труба Ду 500', required=False)
    TDU1000 = forms.IntegerField(label='Труба Ду 1000', required=False)
    UDU500 = forms.IntegerField(label='Угол Ду 500', required=False)
    UDU1000 = forms.IntegerField(label='Угол Ду 1000', required=False)
    TRDU500 = forms.IntegerField(label='Тройник Ду 500', required=False)
    TRDU1000 = forms.IntegerField(label='Тройник Ду 1000', required=False)
    TRP1000_500 = forms.IntegerField(label='Тройник переходной 1000/500', required=False)
    PDU1000_500 = forms.IntegerField(label='Переходник 1000/500', required=False)
    AUTO = forms.IntegerField(label='Автотранспорт', required=False)
    KS = forms.IntegerField(label='КС', required=False)
    GRS = forms.IntegerField(label='ГРС', required=False)