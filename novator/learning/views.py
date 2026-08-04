from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from bank.models import Zakaz, ZakazItem, Balance, HistoryOperation
from main.models import Material, Status, Team
from bank.func import history
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from learning.forms import ZakazFormPremii
from constance import config
from django.db.models import Q

user = get_user_model()

# Create your views here.
def index(request):
    teams = Team.objects.filter(status=True, name__in=request.user.userprofile.teams.values_list('name', flat=True)).order_by('pk')
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
    zakazy_grs = Zakaz.objects.filter(team=team, category__slug='grs')
    zakazy_items_grs = ZakazItem.objects.filter(~Q(start_year=None), zakaz__in=zakazy_grs).order_by('start_year')
    form = ZakazFormPremii()
    return render(request, 'learning/team_detail.html', {'team': team, 
                                                         'zakazy': zakazy, 
                                                         'zakazy_items': zakazy_items, 
                                                         'premii': premii, 
                                                         'zakazy_premii': zakazy_premii, 
                                                         'grs': zakazy_items_grs,
                                                         'form': form})

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
                status=Status.objects.get(name='Завершен'),
                payment=True,
                year=config.YEAR
            )
            ZakazItem.objects.create(
                zakaz=zakaz,
                material=material,
                quantity=1,
                price=material.price
            )
            zakaz.save()
            balance = Balance.objects.get(team=team)
            balance.money += material.price
            balance.save()
            history(operation_type='credit', zakaz=zakaz, price=material.price, balance=balance, description=f'Прибыль от достижения {material.name}')
    # Implementation for creating premii based on the team's achievements
    messages.success(request, f'Достижение успешно оформлено! Сумма {material.price} зачислена на баланс команды')
    return redirect('learning:team_detail', team_id=team.id)


@login_required
def check_new_learning_orders(request):
    teams = Team.objects.filter(status=True, name__in=request.user.userprofile.teams.values_list('name', flat=True))
    zakazy = Zakaz.objects.filter(category__slug='learning', status__pk=2, payment=True, team__in=teams).order_by('-id')[:50]
    data = []
    for zakaz in zakazy:
        items = ZakazItem.objects.filter(zakaz=zakaz)
        material_text = ', '.join(f"{item.material.name}-{int(item.quantity)} шт." for item in items)
        data.append({
            'id': zakaz.id,
            'team_name': zakaz.team.name if zakaz.team else '-',
            'year': zakaz.year,
            'status': zakaz.status.name if zakaz.status else '',
            'description': material_text,
        })
    return JsonResponse({'zakazy': data})


