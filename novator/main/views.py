from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .models import Team
from bank.models import Buy, Balance, Zapusk, Zakaz

# Create your views here.

@login_required
def index(request):
    teams = Team.objects.all()
    context = {
        'teams': teams,
    }
    return render(request, 'main/index.html', context)

@login_required
def team(request, pk):
    team = get_object_or_404(Team, pk=pk)
    buy = Buy.objects.filter(team=team)
    balance = Balance.objects.get(team=team)
    zapusk = Zapusk.objects.filter(team=team)
    zakaz = Zakaz.objects.filter(team=team)
    context = {
        'team': team,
        'buy': buy,
        'zapusk': zapusk,
        'balance': balance,
        'zakaz': zakaz,
    }
    return render(request, 'main/team.html', context)