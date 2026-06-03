from .models import Zakaz, Team, ZakazItem, Material
from django import forms
from django.contrib.auth import get_user_model


def get_choices():
    choices = []
    for instance in Team.objects.filter(status=True):
        choices.append((instance.pk, instance.name))
    return choices

def get_choices_test(choices):
    return choices

def get_shtraf_choices():
    choices = []
    for instance in Material.objects.filter(category__pk=4):
        choices.append((instance.pk, instance.name))
    return choices

def get_grs_choices():
    choices=[]
    for item in Material.objects.filter(category__slug='grs'):
        choices.append((item.pk,item.name))
    return choices

get_ks_bank = lambda: [(item.pk, item.name) for item in Material.objects.filter(category__slug='bank_operations')]

get_ks_choices = lambda: [(item.pk, item.name) for item in Material.objects.filter(category__slug='ks')]

def get_buildings_choices():
    choices=[]
    for item in Material.objects.filter(category__slug='eco'):
        choices.append((item.pk,item.name))
    return choices

KOEFF_CHOICES = (
    (1.0, 'Без скидки'),
    (0.5, 'Скидка 50%'),
    (1.5, 'Наценка 50%'),
    (2.0, 'Наценка 100%'),
    (2.5, 'Наценка 150%'),
    (3.0, 'Наценка 200%'),
)

class ZakazFormBank(forms.Form):
    team = forms.ChoiceField(label='Команда',choices=get_choices(), widget=forms.Select(attrs={'id': 'team-select'}))
    team_balance = forms.IntegerField(label='Узнать баланс', required=False)
    otmena = forms.IntegerField(label='Отмена заказа', required=False)
    koeff = forms.ChoiceField(label='Коэффициент', choices=KOEFF_CHOICES, required=False)
    category = forms.CharField(widget=forms.HiddenInput(), initial='bank_operations')



class ZakazFormTrub(forms.Form):
    team = forms.ChoiceField(label='Команда',choices=get_choices(), widget=forms.Select(attrs={'id': 'team-select'}))
    TDU500 = forms.IntegerField(label='Труба Ду 500', required=False)
    TDU1000 = forms.IntegerField(label='Труба Ду 1000', required=False)
    UDU500 = forms.IntegerField(label='Угол Ду 500', required=False)
    UDU1000 = forms.IntegerField(label='Угол Ду 1000', required=False)
    TRDU500 = forms.IntegerField(label='Тройник Ду 500', required=False)
    TRDU1000 = forms.IntegerField(label='Тройник Ду 1000', required=False)
    TRP1000_500 = forms.IntegerField(label='Тройник переходной 1000/500', required=False)
    PDU1000_500 = forms.IntegerField(label='Переходник 1000/500', required=False)
    TDU500PP = forms.IntegerField(label='Подводный переход ДУ 500', required=False)
    TDU1000PP = forms.IntegerField(label='Подводный переход ДУ 1000', required=False)
    koeff = forms.ChoiceField(label='Коэффициент', choices=KOEFF_CHOICES, required=False)
    category = forms.CharField(widget=forms.HiddenInput(), initial='trubi')
      


class ZakazFormGRS(forms.Form):
    team = forms.ChoiceField(label='Команда', choices=get_choices(), widget=forms.Select(attrs={'id': 'team-select'}))
    building = forms.ChoiceField(label='ГРС', choices=get_grs_choices(), widget=forms.Select(attrs={'id': 'grs-select'}) )
    description = forms.CharField(label='Номер догвора',max_length=10)
    koeff = forms.ChoiceField(label='Коэффициент', choices=KOEFF_CHOICES, required=False)
    category = forms.CharField(widget=forms.HiddenInput(), initial='grs')


class ZakazFormKS(forms.Form):
    team = forms.ChoiceField(label='Команда', choices=get_choices(), widget=forms.Select(attrs={'id': 'team-select'}))
    building = forms.ChoiceField(label='КС', choices=get_ks_choices(), widget=forms.Select(attrs={'id': 'ks-select'}) )
    description = forms.CharField(label='Номер догвора',max_length=10)
    koeff = forms.ChoiceField(label='Коэффициент', choices=KOEFF_CHOICES, required=False)
    category = forms.CharField(widget=forms.HiddenInput(), initial='ks')


class ZakazFormBuildings(forms.Form):
    team = forms.ChoiceField(label='Команда', choices=get_choices(), widget=forms.Select(attrs={'id': 'team-select'}))
    building = forms.ChoiceField(label='Здание', choices=get_buildings_choices(), widget=forms.Select(attrs={'id': 'building-select'}) )
    description = forms.CharField(label='Номер догвора',max_length=10)
    koeff = forms.ChoiceField(label='Коэффициент', choices=KOEFF_CHOICES, required=False)
    category = forms.CharField(widget=forms.HiddenInput(), initial='eco')


class ZakazFormAuto(forms.Form):
    team = forms.ChoiceField(label='Команда', choices=get_choices(), widget=forms.Select(attrs={'id': 'team-select'}))
    auto = forms.IntegerField(label='Транспорт', required=False)
    koeff = forms.ChoiceField(label='Коэффициент', choices=KOEFF_CHOICES, required=False)
    category = forms.CharField(widget=forms.HiddenInput(), initial='auto')

class ZakazFormObuchenie(forms.Form):
    team = forms.ChoiceField(label='Команда', choices=get_choices(), widget=forms.Select(attrs={'id': 'team-select'}))
    learn_les = forms.BooleanField(label='Мастер ЛЭС', required=False)
    learn_grs = forms.BooleanField(label='Оператор ГРС', required=False)
    learn_ks = forms.BooleanField(label='Инженер ГКС', required=False)
    koeff = forms.ChoiceField(label='Коэффициент', choices=KOEFF_CHOICES, required=False)
    category = forms.CharField(widget=forms.HiddenInput(), initial='obuchenie')


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
    shtraf_11 = forms.IntegerField(label='Штраф 11', required=False)
    shtraf_12 = forms.IntegerField(label='Штраф 12', required=False)
    shtraf_13 = forms.IntegerField(label='Штраф 13', required=False)
    shtraf_14 = forms.IntegerField(label='Штраф 14', required=False)
    shtraf_15 = forms.IntegerField(label='Штраф 15', required=False)
    shtraf_16 = forms.IntegerField(label='Штраф 16', required=False)
    koeff = forms.ChoiceField(label='Коэффициент', choices=KOEFF_CHOICES, required=False)
    category = forms.CharField(widget=forms.HiddenInput(), initial='shtrafs')


class ZakazFormCredit(forms.Form):
    team = forms.ChoiceField(label='Команда', choices=get_choices(), widget=forms.Select(attrs={'id': 'team-select'}))
    amount = forms.FloatField(label='Сумма кредита', required=True)
    #year = forms.IntegerField(label='Год кредита', required=True)
    percent = forms.FloatField(label='Процентная ставка', required=True)


class PremiaForm(forms.Form):
    team = forms.ChoiceField(label='Команда', choices=get_choices(), widget=forms.Select(attrs={'id': 'team-select'}))
    amount = forms.FloatField(label='Сумма премии', required=True)
    #year = forms.IntegerField(label='Год премии', required=True)


class KapremontForm(forms.Form):
    team = forms.ChoiceField(label='Команда', choices=get_choices(), widget=forms.Select(attrs={'id': 'team-select'}))
    kap_rem = forms.IntegerField(label='Капремонт', required=True, initial=1)
    TDU500 = forms.IntegerField(label='Труба Ду 500', required=False)
    TDU1000 = forms.IntegerField(label='Труба Ду 1000', required=False)
    UDU500 = forms.IntegerField(label='Угол Ду 500', required=False)
    UDU1000 = forms.IntegerField(label='Угол Ду 1000', required=False)
    TRDU500 = forms.IntegerField(label='Тройник Ду 500', required=False)
    TRDU1000 = forms.IntegerField(label='Тройник Ду 1000', required=False)
    TRP1000_500 = forms.IntegerField(label='Тройник переходной 1000/500', required=False)
    PDU1000_500 = forms.IntegerField(label='Переходник 1000/500', required=False)
    TDU500PP = forms.IntegerField(label='Подводный переход ДУ 500', required=False)
    TDU1000PP = forms.IntegerField(label='Подводный переход ДУ 1000', required=False)
    kap_rem_du500 = forms.IntegerField(label='Капремонт Ду 500', required=False)
    kap_rem_du1000 = forms.IntegerField(label='Капремонт Ду 1000', required=False)
    kap_rem_ugol_du500 = forms.IntegerField(label='Капремонт Угол Ду 500', required=False)
    kap_rem_ugol_du1000 = forms.IntegerField(label='Капремонт Угол Ду 1000', required=False)
    kap_rem_tr_du500 = forms.IntegerField(label='Капремонт Тройник Ду 500', required=False)
    kap_rem_tr_du1000 = forms.IntegerField(label='Капремонт Тройник Ду 1000', required=False)
    kap_rem_pr = forms.IntegerField(label='Капремонт Переходинк 1000/500', required=False)
    koeff = forms.ChoiceField(label='Коэффициент', choices=KOEFF_CHOICES, required=False)
    category = forms.CharField(widget=forms.HiddenInput(), initial='trubi')
    