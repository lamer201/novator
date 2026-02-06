from .models import Zakaz, Team, ZakazItem
from django import forms

def get_choices():
    choices = []
    for instance in Team.objects.filter(status=True):
        choices.append((instance.pk, instance.name))
    return choices


class ZakazFormTrub(forms.Form):
    team = forms.ChoiceField(label='Команда', choices=get_choices())
    TDU500 = forms.IntegerField(label='Труба Ду 500', required=False)
    TDU1000 = forms.IntegerField(label='Труба Ду 1000', required=False)
    UDU500 = forms.IntegerField(label='Угол Ду 500', required=False)
    UDU1000 = forms.IntegerField(label='Угол Ду 1000', required=False)
    TRDU500 = forms.IntegerField(label='Тройник Ду 500', required=False)
    TRDU1000 = forms.IntegerField(label='Тройник Ду 1000', required=False)
    TRP1000_500 = forms.IntegerField(label='Тройник переходной 1000/500', required=False)
    PDU1000_500 = forms.IntegerField(label='Переходник 1000/500', required=False)


class ZakazFormKSGRS(forms.Form):
    team = forms.ChoiceField(label='Команда', choices=get_choices())
    KS = forms.IntegerField(label='КС', required=False)
    GRS = forms.IntegerField(label='ГРС', required=False)


class ZakazFormAuto(forms.Form):
    team = forms.ChoiceField(label='Команда', choices=get_choices())
    auto = forms.IntegerField(label='Транспорт', required=False)


class ZakazFormObuchenie(forms.Form):
    team = forms.ChoiceField(label='Команда', choices=get_choices())
    master_les = forms.IntegerField(label='Мастер ЛЭС', required=False)
    master_grs = forms.IntegerField(label='Мастер ГРС', required=False)
    master_ks = forms.IntegerField(label='Мастер КС', required=False)
