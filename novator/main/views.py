from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction
from bank.models import Balance, Zakaz
from main.models import Status, Team
from bank.func import give_money
from mtr.models import Stock

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
    stock_by_skalad = Stock.objects.filter(warehouse__team='')
    return render(request, 'main/control.html', {'teams': teams, 'stock': stock, 'stock_by_skalad': stock_by_skalad})