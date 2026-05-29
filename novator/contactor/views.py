from django.shortcuts import redirect, render
from django.contrib import messages
from .models import EcoCompensation, EcoCompensationOperation
from main.models import Team
from bank.models import Zakaz, ZakazItem
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib.auth import get_user_model

user = get_user_model()


# Create your views here.
def index(request):
    teams = Team.objects.filter(status=True, name__in=request.user.userprofile.teams.values_list('name', flat=True))
    return render(request, 'contactor/index.html', {'teams': teams})

def team_detail(request, team_id):
    team = Team.objects.get(id=team_id)
    zakazy = Zakaz.objects.filter(team=team, category__slug__in=['trubi','ks','grs'])
    zakazy_items = ZakazItem.objects.filter(zakaz__in=zakazy)
    return render(request, 'contactor/team_detail.html', {'team': team, 'zakazy': zakazy, 'zakazy_items': zakazy_items})

@login_required
@transaction.atomic
def create_eco_compensation(request, zakaz_id):
    zakaz = Zakaz.objects.get(id=zakaz_id)
    team = Team.objects.get(pk=zakaz.team.id)
    eco_compensation = 0
    for item in ZakazItem.objects.filter(zakaz=zakaz):
        eco_compensation += (item.material.eco_compensations.amount * item.quantity) if item.material.eco_compensations else 0
    team.eco_scores.score += eco_compensation
    team.save()
    eco_compensation = EcoCompensationOperation.objects.create(
        zakaz=zakaz,
        eco_compensation=eco_compensation,
        description=f'Компенсация за заказ {zakaz.id} с эко-оценкой {eco_compensation}'
    )
    messages.success(request, 'Компенсация успешно оформлена!')
    return redirect('contactor:team_detail', team_id=team.id)