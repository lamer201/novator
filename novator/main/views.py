from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction
from bank.models import Balance, Zakaz, ZakazItem
from main.models import Status, Team, ItemProperty
from bank.func import give_money, calculate_win_score
from mtr.models import Stock, Sklad, Shipment
from django.db.models import Sum
from .models import Team
from bank.models import Balance, Zakaz
from constance import config

# Create your views here.

@login_required
def index(request):
    teams = Team.objects.all()
    context = {
        'teams': teams,
        'year': config.YEAR,

    }
    return render(request, 'main/index.html', context)

@login_required
def team(request, pk):
    team = get_object_or_404(Team, pk=pk)
    balance = Balance.objects.get(team=team)
    zakaz = Zakaz.objects.filter(team=team)
    context = {
        'team': team,
        'balance': balance,
        'zakaz': zakaz,
    }
    return render(request, 'main/team.html', context)

@login_required
@transaction.atomic
def next_year(request):
    if request.method == 'POST':
        config.YEAR = request.POST.get('year', config.YEAR)
        for team in Team.objects.filter(status=True):
            give_money(team)
    return render(request, 'main/next_year.html', {'year': config.YEAR})


def control(request):
    teams = Team.objects.filter(status=True)
    stock = Stock.objects.filter(warehouse__team__in=teams)
    sklad = Sklad.objects.filter(is_active=True, team=None)
    stock_by_skalad = Stock.objects.filter(warehouse__in=sklad, material__category__slug__in=['trubi', 'ks', 'eco'])
    stock_by_skalad_grs = Shipment.objects.filter(from_warehouse__in=sklad, material__category__slug='grs').count()
    zakaz_items_premii = ZakazItem.objects.filter(material__category__slug='premii')
    bally = ItemProperty.objects.filter(property_name='winner_score')

    teams_items = []
    teams_grs = []
    win_score = []
    total_potrebiteli = []
    for team in teams:
        total_potrebitel = 0
        team_stock = Stock.objects.filter(warehouse__team=team)
        win_score.append({'team': team, 'score': calculate_win_score(team)}) 
        total = team_stock.filter(material__category__slug='trubi').aggregate(total=Sum('quantity'))['total'] or 0
        total_grs = team_stock.filter(material__category__slug='grs').aggregate(total=Sum('quantity'))['total'] or 0
        for grs in ZakazItem.objects.filter(zakaz__team=team, material__category__slug='grs', zakaz__status__pk=5):
            total_potrebitel += float(ItemProperty.objects.get(material=grs.material, property_name='potrebitel').property_value)
        total_potrebiteli.append({'team': team, 'total_potrebitel': total_potrebitel})
        teams_items.append({'team': team, 'items_count': total * 20})
        teams_grs.append({'team': team, 'total_grs': total_grs})
    return render(request, 'main/control.html', {'teams': teams,
                                                  'sklad': sklad,
                                                    'stock': stock,
                                                      'stock_by_skalad': stock_by_skalad,
                                                        'teams_items': teams_items,
                                                          'teams_grs': teams_grs,
                                                            'stock_by_skalad_grs': stock_by_skalad_grs,
                                                              'win_score': win_score,
                                                                'zakaz_items_premii': zakaz_items_premii,
                                                                'bally': bally,
                                                                'total_potrebiteli': total_potrebiteli})