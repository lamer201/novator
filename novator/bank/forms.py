from .models import Zakaz, Team, ZakazItem, Material
from django import forms

def get_choices():
    choices = []
    for instance in Team.objects.filter(status=True):
        choices.append((instance.pk, instance.name))
    return choices

def get_shtraf_choices():
    choices = []
    for instance in Material.objects.filter(category__pk=4):
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

class ZakazFormTrub(forms.Form):
    team = forms.ChoiceField(label='Команда', choices=get_choices(), widget=forms.Select(attrs={'id': 'team-select'}))
    TDU500 = forms.IntegerField(label='Труба Ду 500', required=False)
    TDU1000 = forms.IntegerField(label='Труба Ду 1000', required=False)
    UDU500 = forms.IntegerField(label='Угол Ду 500', required=False)
    UDU1000 = forms.IntegerField(label='Угол Ду 1000', required=False)
    TRDU500 = forms.IntegerField(label='Тройник Ду 500', required=False)
    TRDU1000 = forms.IntegerField(label='Тройник Ду 1000', required=False)
    TRP1000_500 = forms.IntegerField(label='Тройник переходной 1000/500', required=False)
    PDU1000_500 = forms.IntegerField(label='Переходник 1000/500', required=False)
    koeff = forms.ChoiceField(label='Коэффициент', choices=KOEFF_CHOICES, required=False)


class ZakazFormKSGRS(forms.Form):
    team = forms.ChoiceField(label='Команда', choices=get_choices(), widget=forms.Select(attrs={'id': 'team-select'}))
    KS = forms.IntegerField(label='КС', required=False)
    GRS = forms.IntegerField(label='ГРС', required=False)
    koeff = forms.ChoiceField(label='Коэффициент', choices=KOEFF_CHOICES, required=False)


class ZakazFormAuto(forms.Form):
    team = forms.ChoiceField(label='Команда', choices=get_choices(), widget=forms.Select(attrs={'id': 'team-select'}))
    auto = forms.IntegerField(label='Транспорт', required=False)
    koeff = forms.ChoiceField(label='Коэффициент', choices=KOEFF_CHOICES, required=False)


class ZakazFormObuchenie(forms.Form):
    team = forms.ChoiceField(label='Команда', choices=get_choices(), widget=forms.Select(attrs={'id': 'team-select'}))
    master_les = forms.IntegerField(label='Мастер ЛЭС', required=False)
    master_grs = forms.IntegerField(label='Мастер ГРС', required=False)
    master_ks = forms.IntegerField(label='Мастер КС', required=False)
    koeff = forms.ChoiceField(label='Коэффициент', choices=KOEFF_CHOICES, required=False)


class ZakazFormShtraf(forms.Form):
    team = forms.ChoiceField(label='Команда', choices=get_choices(), widget=forms.Select(attrs={'id': 'team-select'}))
    #shtraf = forms.ChoiceField(label='Штраф', required=True, choices=get_shtraf_choices())
    shtraf_1 = forms.IntegerField(label='Штраф 1', required=False)
    shtraf_2 = forms.IntegerField(label='Штраф 2', required=False)
    shtraf_3 = forms.IntegerField(label='Штраф 3', required=False)
    shtraf_4 = forms.IntegerField(label='Штраф 4', required=False)
    shtraf_5 = forms.IntegerField(label='Штраф 5', required=False)
    shtraf_6 = forms.IntegerField(label='Штраф 6', required=False)
    shtraf_7 = forms.IntegerField(label='Штраф 7', required=False)
    shtraf_8 = forms.IntegerField(label='Штраф 8', required=False)
    shtraf_9 = forms.IntegerField(label='Штраф 9', required=False)
    shtraf_10 = forms.IntegerField(label='Штраф 10', required=False)
    koeff = forms.ChoiceField(label='Коэффициент', choices=KOEFF_CHOICES, required=False)