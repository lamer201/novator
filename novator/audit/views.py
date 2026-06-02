from django.shortcuts import render
from mtr.models import Team
from django.contrib.auth import get_user_model
from audit.forms import ShtrafForm
from bank.models import Zakaz, ZakazItem
from main.models import Category, Material, Status
from django.contrib.auth.decorators import login_required
from django.db import transaction
from constance import config

user = get_user_model()

# Create your views here.
def index(request):
    teams = Team.objects.filter(status=True, name__in=request.user.userprofile.teams.values_list('name', flat=True))

    return render(request, 'audit/index.html', {'teams': teams})

def team_detail(request, team_id):
    team = Team.objects.get(id=team_id)
    return render(request, 'audit/team_detail.html', {'team': team})

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
        return render(request, 'audit/shtraf.html', {'team': team, 'message': message})
    form = ShtrafForm()
    return render(request, 'audit/shtraf.html', {'form': form})
