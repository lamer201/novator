from decimal import Decimal
from urllib import request

from django.shortcuts import redirect, render
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Extradition, Sklad, Shipment, Material, Stock
from main.models import Status, Team
from bank.models import Zakaz, ZakazItem
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Sum


user = get_user_model()


def check_obuchenie(zakaz):
    team = zakaz.team
    if zakaz.category.slug == 'trubi' and team.learn_les:
        return True
    elif zakaz.category.slug == 'grs' and team.learn_grs:
        return True
    elif zakaz.category.slug == 'ks' and team.learn_ks:
        return True
    else:
        return False

@login_required
def index(request):
    zakazy = Zakaz.objects.filter(status__pk=2,payment=True,issued=False,category__slug__in=['trubi', 'ks', 'grs'], team__name__in=request.user.userprofile.teams.values_list('name', flat=True)) 
    zakazy_items = ZakazItem.objects.filter(zakaz__in=zakazy)
    sklad = Sklad.objects.filter(is_active=True, name = request.user.userprofile.sklad)
    stock = Stock.objects.filter(warehouse__in=sklad, material__category__slug__in=['trubi', 'ks'])
    teams = Team.objects.filter(status=True, name__in=request.user.userprofile.teams.values_list('name', flat=True))
    grs_items = Stock.objects.filter(warehouse__team__in=teams, material__category__slug='grs').count()
    teams_items = []
    teams_auto = []

    # calculate total quantity of items in each team's sklad(s)
    for team in teams:
        team_sklads = Sklad.objects.filter(team=team, is_active=True)
        items_auto = ZakazItem.objects.filter(zakaz__team=team, material__category__slug__in=['auto']).aggregate(total=Sum('quantity'))['total'] or 0
        teams_auto.append({'team': team, 'auto_count': items_auto})
        total = Stock.objects.filter(warehouse__in=team_sklads, material__category__slug__in=['trubi']).aggregate(total=Sum('quantity'))['total'] or 0
        teams_items.append({'team': team, 'items_count': total * 20})

    materials = []
    for items in sklad:
        materials.extend(Stock.objects.filter(warehouse=items))
    context = {
        'zakazy': zakazy,
        'zakazy_items': zakazy_items,
        'sklad': stock,
        'teams': teams,
        'materials': materials,
        'teams_items': teams_items,
        'teams_auto': teams_auto,
        'grs_items': grs_items,
    }
    return render(request, 'mtr/index.html', context)

@login_required
def sklad(request):
    sklad = Sklad.objects.all()
    context = {
        'sklad': sklad,
    }
    return render(request, 'mtr/sklad.html', context)


@login_required
def extraditions(request):  
    extraditions = Extradition.objects.all()
    context = {
        'extraditions': extraditions,
    }
    return render(request, 'mtr/extraditions.html', context)

@login_required
def extradition_detail(request, pk):
    if request.method == 'POST':
        pass
    zakaz = Zakaz.objects.get(pk=pk)
    material = ZakazItem.objects.filter(zakaz=zakaz)
    context = {
        'zakaz': zakaz,
        'material': material
    }
    return render(request, 'mtr/extradition_detail.html', context)

@login_required
def sklad_teams(request) :
    sklad = Sklad.objects.filter(team__isnull=False, is_active=True)
    materials = []
    for items in sklad:
        materials.extend(Stock.objects.filter(warehouse=items))
    context = {
        'sklad': sklad,
        'materials': materials
    }
    return render(request, 'mtr/sklad_teams.html', context)


def sklad_team_detail(request, pk):
    team = Team.objects.get(pk=pk)
    sklad = Sklad.objects.get(pk=team.sklad.pk)
    materials = Stock.objects.filter(warehouse=sklad)
    context = {
        'sklad': sklad,
        'materials': materials
    }
    return render(request, 'mtr/sklad_team_detail.html', context)

@transaction.atomic 
def shipment(request, pk):
    zakaz = Zakaz.objects.get(pk=pk)
    if not check_obuchenie(zakaz):
        messages.error(request, 'Команда не обучена для перемещения данного типа материалов.')
        return redirect('mtr:index')
    if zakaz.issued == True:
        messages.error(request, 'Перемещение уже совершено измените статус заказа вручную.')
        return render(request, 'mtr/index.html')
    material = ZakazItem.objects.filter(zakaz=zakaz)
    sklad_from = Sklad.objects.get(name=request.user.userprofile.sklad)
    sklad_to = Sklad.objects.get(team=zakaz.team)
    if material.filter(material__category__slug='trubi').exists():
        zakazy = Zakaz.objects.filter(team=zakaz.team)
        auto_team = ZakazItem.objects.filter(zakaz__in=zakazy, material__category__slug='auto').aggregate(total=Sum('quantity'))['total'] or 0
        team_total_km = Stock.objects.filter(warehouse__team=zakaz.team, material__category__slug='trubi').aggregate(total=Sum('quantity'))['total'] or 0
        if zakaz.total_eco_score > zakaz.team.eco_scores.score:
            messages.error(request, 'Недостаточно очков экологии для перемещения.')
            return redirect('mtr:index')
        if (15 * (auto_team +1)) / ((zakaz.total_items + team_total_km)) < 1:
            messages.error(request, f'Недостаточно автотранспорта. У команды {auto_team} ед. автотранспорта, {zakaz.total_items * 20} - всего км для перемещения, {team_total_km * 20} - всего км у команды.')
            return redirect('mtr:index')
    for item in material:
        material_mtr = Material.objects.get(pk=item.material.pk)
        shipment = Shipment(
        from_warehouse=sklad_from,
        to_warehouse=sklad_to,
        material=material_mtr,
        quantity=item.quantity,  # Укажите нужное количество
        description="Перемещение по заказу №123"
        )
        try:
            shipment.perform_shipment()
            print("Перемещение выполнено")
        except ValidationError as e:
            print("Ошибка:", e)
    team = Team.objects.get(pk=zakaz.team.pk)
    team.eco_scores.score -= zakaz.total_eco_score
    team.eco_scores.save()
    zakaz.issued = True
    zakaz.status = Status.objects.get(pk=3)
    zakaz.save()
    messages.success(request, 'Перемещение успешно выполнено.')
    return redirect('mtr:index')