from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Extradition, Sklad, Shipment, Material, Stock
from main.models import Status
from bank.models import Zakaz, ZakazItem
from django.core.exceptions import ValidationError


user = get_user_model()

@login_required
def index(request):
    zakazy = Zakaz.objects.filter(status__pk=2).filter(payment=True).filter(issued=False)
    sklad = Sklad.objects.filter(is_active=True, name = request.user.userprofile.sklad)
    stock = Stock.objects.filter(warehouse__in=sklad, material__category__slug__in=['trubi', 'buildings'])
    sklad_teams = Sklad.objects.filter(team__isnull=False)
    materials = []
    for items in sklad:
        materials.extend(Stock.objects.filter(warehouse=items))
    context = {
        'zakazy': zakazy,
        'sklad': stock,
        'sklad_teams': sklad_teams,
        'materials': materials
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
    sklad = Sklad.objects.filter(team__isnull=False, active=True)
    materials = []
    for items in sklad:
        materials.extend(Stock.objects.filter(sklad=items))
    context = {
        'sklad': sklad,
        'materials': materials
    }
    return render(request, 'mtr/sklad_teams.html', context)


def sklad_team_detail(request, pk):
    sklad = Sklad.objects.get(pk=pk)
    materials = Stock.objects.filter(warehouse=sklad)
    context = {
        'sklad': sklad,
        'materials': materials
    }
    return render(request, 'mtr/sklad_team_detail.html', context)

def shipment(request, pk):
    zakaz = Zakaz.objects.get(pk=pk)
    if zakaz.issued == True:
        messages.error(request, 'Перемещение уже совершено измените статус заказа вручную.')
        return render(request, 'mtr/index.html')
    material = ZakazItem.objects.filter(zakaz=zakaz)
    sklad_from = Sklad.objects.get(slug='sklad-1')
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

    zakaz.issued = True
    zakaz.status = Status.objects.get(pk=3)
    zakaz.save()
    return render(request, 'mtr/index.html')