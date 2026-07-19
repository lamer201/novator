from django.shortcuts import render, get_object_or_404, redirect
from mtr.models import Team
from django.contrib.auth import get_user_model
from django.contrib import messages
from audit.forms import ShtrafForm
from bank.models import Zakaz, ZakazItem
from main.models import Category, Material, Status, ItemProperty
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction
from constance import config

user = get_user_model()

# Create your views here.
def index(request):
    teams = Team.objects.filter(status=True, name__in=request.user.userprofile.teams.values_list('name', flat=True)).order_by('pk')

    return render(request, 'audit/index.html', {'teams': teams})

def team_detail(request, team_id):
    team = Team.objects.get(id=team_id)
    zakazy = Zakaz.objects.filter(team=team,category__slug='grs')
    items = ZakazItem.objects.filter(zakaz__in=zakazy).order_by('zakaz_id')
    grs = Material.objects.filter(category__slug='grs')
    return render(request, 'audit/team_detail.html', {'team': team,
                                                      'zakazy': zakazy,
                                                      'items': items,
                                                      'grs': grs
                                                      })

def team_audit(request, team_id):
    team = Team.objects.get(id=team_id)
    return render(request, 'audit/team_audit.html', {'team': team})


@login_required
@transaction.atomic
def shtraf(request):
    if request.method == 'POST':
        form = ShtrafForm(request.POST)
        if form.is_valid():
            team_id = form.cleaned_data['team']
            team = Team.objects.get(id=team_id)
            shtraf_id = form.cleaned_data['shtraf']
            shtraf = Material.objects.get(id=shtraf_id)
            zakaz = Zakaz.objects.create(team=team, 
                                        category=Category.objects.get(slug='shtrafs'),
                                        description=shtraf.name,
                                        year=config.YEAR,
                                        month=0,
                                        status=Status.objects.get(pk=1))
            zakaz_item = ZakazItem.objects.create(zakaz=zakaz, material=shtraf, quantity=1, price=shtraf.price)
            zakaz.save()
            message = f'Штраф "{shtraf.name}" успешно добавлен для команды "{team.name}".'
            # Здесь можно добавить логику для обработки штрафа, например, сохранение в базе данных
            # Например:
            # Shtraf.objects.create(team=team, amount=amount, reason=reason)
            return render(request, 'audit/shtraf.html', {'team': team, 'message': message, 'form': form})
    form = ShtrafForm()
    return render(request, 'audit/shtraf.html', {'form': form})


@login_required
@require_POST
def zapusk_edit(request):
    if request.method == 'POST':
        zakaz_item_id = request.POST.get('zakaz_item')
        profit_koeff = request.POST.get('koeff_val')
        zakaz_item = get_object_or_404(ZakazItem, pk=zakaz_item_id)
        team = Team.objects.get(pk=zakaz_item.zakaz.team.pk)
        old_material = zakaz_item.material
        team.eco_scores.score += old_material.eco_score
        material = Material.objects.get(pk=request.POST.get('material_item'))
        zakaz_item.material = material
        team.eco_scores.score -= material.eco_score
        team.eco_scores.save()
        profit = ItemProperty.objects.get(material=material, property_name='cost').property_value
        zakaz_item.profit_val = profit
        try:
            if profit_koeff is not None:
                zakaz_item.profit_koeff = float(profit_koeff)
            zakaz_item.save()
            messages.success(request, f'Позиция успешно обновлена. Очков экологии добавилось:{old_material.eco_score}, Очков экологии убавилось: {material.eco_score}')
        except (ValueError, TypeError):
            messages.error(request, 'Неверные значения коэффициента прибыли. Пожалуйста, введите корректные данные.')
    return redirect('audit:team_detail', team_id=zakaz_item.zakaz.team.pk)