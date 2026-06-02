from django.contrib import messages
from django.shortcuts import redirect, render
from bank.models import Zakaz, ZakazItem
from main.models import Material, Status, Team
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from learning.forms import ZakazFormPremii
from constance import config

user = get_user_model()

# Create your views here.
def index(request):
    teams = Team.objects.filter(status=True, name__in=request.user.userprofile.teams.values_list('name', flat=True))
    zakazy = Zakaz.objects.filter(category__slug='learning', status__pk=2, payment=True, team__in=teams)
    zakazy_items = ZakazItem.objects.filter(zakaz__in=zakazy)
    return render(request, 'learning/index.html', {'teams': teams, 'zakazy': zakazy, 'zakazy_items': zakazy_items})


def team_detail(request, team_id):
    if request.method == 'POST':
        return create_premii(request, team_id)
    team = Team.objects.get(id=team_id)
    zakazy = Zakaz.objects.filter(team=team, category__slug='learning')
    zakazy_items = ZakazItem.objects.filter(zakaz__in=zakazy)
    zakazy_premii = Zakaz.objects.filter(team=team, category__slug='premii')
    premii = ZakazItem.objects.filter(zakaz__in=zakazy_premii)
    form = ZakazFormPremii()
    return render(request, 'learning/team_detail.html', {'team': team, 'zakazy': zakazy, 'zakazy_items': zakazy_items, 'premii': premii, 'zakazy_premii': zakazy_premii, 'form': form})

@login_required
@transaction.atomic
def success_learning(request, zakaz_id):
    zakaz = Zakaz.objects.get(id=zakaz_id)
    zakaz.status = Status.objects.get(name='Завершен')
    team = Team.objects.get(id=zakaz.team.id)
    zakaz.save()
    zakaz_items = ZakazItem.objects.filter(zakaz=zakaz)
    for item in zakaz_items:
        if item.material.slug == 'learn_ks':
            team.learn_ks = True
        if item.material.slug == 'learn_grs':
            team.learn_grs = True
        if item.material.slug == 'learn_les':
            team.learn_les = True
    team.save()
    messages.success(request, 'Обучение успешно завершено!')
    return redirect('learning:index')


@login_required
@transaction.atomic
def create_premii(request, team_id):
    team = Team.objects.get(id=team_id)
    if request.method == 'POST':
        form = ZakazFormPremii(request.POST)
        if form.is_valid():
            material_id = form.cleaned_data['material']
            material = Material.objects.get(id=material_id)
            zakaz = Zakaz.objects.create(
                team=team,
                category=material.category,
                status=Status.objects.get(name='Создан'),
                payment=False,
                year=config.YEAR
            )
            ZakazItem.objects.create(
                zakaz=zakaz,
                material=material,
                quantity=1,
                price=material.price
            )
            zakaz.save()
    # Implementation for creating premii based on the team's achievements
    messages.success(request, 'Достижение успешно оформлено!')
    return redirect('learning:team_detail', team_id=team.id)