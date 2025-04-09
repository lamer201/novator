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

def team(request, pk):
    team = get_object_or_404(Team, pk=pk)
    buy = Buy.objects.filter(team=pk)
    balance = get_object_or_404(Balance, team=pk)
    zapusk = Zapusk.objects.filter(team=pk)
    zakaz = Zakaz.objects.filter(team=pk)
    context = {
        'team': team,
        'buy': buy,
        'zapusk': zapusk,
        'balance': balance,
        'zakaz': zakaz,
    }
    return render(request, 'main/team.html', context)