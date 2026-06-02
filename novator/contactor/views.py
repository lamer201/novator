from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.contrib import messages
from mtr.models import Shipment, Sklad, Stock
from .models import EcoCompensation, EcoCompensationOperation
from main.models import Material, Status, Team, EcoScore
from bank.models import Zakaz, ZakazItem
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib.auth import get_user_model

user = get_user_model()


# Create your views here.
def index(request):
    zakazy = Zakaz.objects.filter(status__pk=2,payment=True,issued=False,category__slug='eco', team__name__in=request.user.userprofile.teams.values_list('name', flat=True))
    zakazy_items = ZakazItem.objects.filter(zakaz__in=zakazy)
    teams = Team.objects.filter(status=True, name__in=request.user.userprofile.teams.values_list('name', flat=True))
    return render(request, 'contactor/index.html', {'teams': teams, 'zakazy': zakazy, 'zakazy_items': zakazy_items})

def team_detail(request, team_id):
    team = Team.objects.get(id=team_id)
    zakazy = Zakaz.objects.filter(team=team, category__slug__in=['trubi','ks','grs'])
    zakazy_items = ZakazItem.objects.filter(zakaz__in=zakazy)
    stock = Stock.objects.filter(warehouse__team=team, material__category__slug='eco')
    return render(request, 'contactor/team_detail.html', {'team': team, 'zakazy': zakazy, 'zakazy_items': zakazy_items, 'stock': stock})

@login_required
@transaction.atomic
def create_eco_compensation(request, zakaz_id):
    zakaz = Zakaz.objects.get(id=zakaz_id)
    team = Team.objects.get(pk=zakaz.team.id)
    eco_score = EcoScore.objects.get(team=team)
    eco_compensation = 0
    for item in ZakazItem.objects.filter(zakaz=zakaz):
        eco_compensation += (item.material.eco_compensations.amount * item.quantity)
    try:
        eco_score.score += eco_compensation
        eco_score.save()
    except Exception as e:
        messages.error(request, f'Ошибка при оформлении компенсации: {e}')
        return redirect('contactor:team_detail', team_id=team.id)
    eco_compensation_operation = EcoCompensationOperation.objects.create(
        zakaz=zakaz,
        eco_compensation=eco_compensation,
        description=f'Компенсация за заказ {zakaz.id} с эко-оценкой {eco_compensation}'
    )
    eco_compensation_operation.save()
    messages.success(request, 'Компенсация успешно оформлена!')
    return redirect('contactor:team_detail', team_id=team.id)


@transaction.atomic 
def shipment(request, pk):
    zakaz = Zakaz.objects.get(pk=pk)
    if zakaz.issued == True:
        messages.error(request, 'Перемещение уже совершено измените статус заказа вручную.')
        return render(request, 'mtr/index.html')
    material = ZakazItem.objects.filter(zakaz=zakaz)
    sklad_from = Sklad.objects.get(name=request.user.userprofile.sklad)
    sklad_to = Sklad.objects.get(team=zakaz.team)
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
    team.eco_scores.score += zakaz.total_eco_score
    team.eco_scores.save()
    zakaz.issued = True
    zakaz.status = Status.objects.get(pk=3)
    zakaz.save()
    eco_compensation = EcoCompensationOperation.objects.create(
        zakaz=zakaz,
        eco_compensation=zakaz.total_eco_score,
        description=f'Компенсация за перемещение заказа {zakaz.id} с эко-оценкой {zakaz.total_eco_score}'
    )
    eco_compensation.save()
    messages.success(request, 'Перемещение успешно выполнено.')
    return redirect('contactor:index')