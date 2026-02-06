from django.shortcuts import get_list_or_404, render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .froms import ZakazFormAuto, ZakazFormObuchenie, ZakazFormTrub, ZakazFormKSGRS
from .models import Balance, Buy, Team, Zakaz, Material, ZakazItem, Status

User = get_user_model()

def get_sum(form, balance):
    sum_material=0
    for field, quantity in form.cleaned_data.items():
        if field != 'team' and quantity:
                    material = get_list_or_404(Material, slug=field)[0]
                    sum_material = sum_material + (material.price*quantity)
        if balance.money < sum_material: 
             return 0
    return sum_material
def check_balance(team): 
    pass

def make_zakaz(form):
    # Get form data
    team = Team.objects.get(pk=form.cleaned_data['team']) 
    balance = Balance.objects.get(team=team)           
    test_balance = get_sum(form, balance)
    if test_balance == 0:
            payment=False
    else:        payment=True
            
    # Create new order
    zakaz = Zakaz.objects.create(
        team=team,
        year = 1,
        month = 0,
        payment=payment,
        status=Status.objects.get(name='Создан')
    )
    zakaz.save()
            
    for field, quantity in form.cleaned_data.items():
        if field != 'team' and quantity:
            material = get_list_or_404(Material, slug=field)[0]
            zakazItem = ZakazItem.objects.create(
                zakaz=zakaz,
                material=material,
                price=material.price,
                quantity=quantity
            )
            zakazItem.save()
    new_balance = balance.money - test_balance
    balance.money = new_balance
    balance.save()
    return redirect('bank:zakaz_detail', zakaz_id=zakaz.pk)  # Replace with your success URL

@login_required
def create_zakaz(request):
    if request.method == 'POST':
        form = ZakazFormTrub(request.POST)
        if form.is_valid():
            return make_zakaz(form)
    else:
        form = ZakazFormTrub()
    
    return render(request, 'bank/zakaz.html', {'form': form})

@login_required
def create_zakaz_ks(request):
    if request.method == 'POST':
        form = ZakazFormKSGRS(request.POST)
        if form.is_valid():
            return make_zakaz(form)
    else:
        form = ZakazFormKSGRS()
    
    return render(request, 'bank/zakaz.html', {'form': form})

@login_required
def zakaz_auto(request):
    if request.method == 'POST':
        form = ZakazFormAuto(request.POST)
        if form.is_valid():
            return make_zakaz(form)
    else:
        form = ZakazFormAuto()
    
    return render(request, 'bank/zakaz.html', {'form': form})

@login_required
def create_zakaz_obuchenie(request):
    if request.method == 'POST':
        form = ZakazFormObuchenie(request.POST)
        if form.is_valid():
            return make_zakaz(form)
    else:
        form = ZakazFormObuchenie()
    
    return render(request, 'bank/zakaz.html', {'form': form})

@login_required
def zakaz_edit(request, zakaz):
     pass


@login_required
def zakaz_list(request):
    if request.GET.get('team'):
        zakazy = Zakaz.objects.filter(team=request.GET.get('team')).order_by('-id')
    else:
        zakazy = Zakaz.objects.all().order_by('-id')
    return render(request, 'bank/zakaz_list.html', {'zakazy': zakazy})

@login_required
def zakaz_detail(request, zakaz_id):
    zakaz = get_list_or_404(Zakaz, pk=zakaz_id)[0]
    items = ZakazItem.objects.filter(zakaz=zakaz)
    return render(request, 'bank/zakaz_detail.html', {'zakaz': zakaz, 'items': items})

def bank_list(request):
    teams = Team.objects.filter(status=True)
    
    list_teams = {}
    for team in teams:
        zakaz = Zakaz.objects.filter(team=team).count
        balance = Balance.objects.get(team=team)
        list_teams.update({team.pk: {'name': team.name, 'balance': balance.money, 'zakaz': zakaz}})
    context = {
        'teams': list_teams
    }
    return render(request, 'bank/bank.html', context)
def team_detail(request, team_id):
    team = get_list_or_404(Team, pk=team_id)[0]
    balance = Balance.objects.get(team=team)
    zakazy = Zakaz.objects.filter(team=team)
    context = {
        'team': team,
        'balance': balance.money,
        'zakazy': zakazy,
    }
    return render(request, 'bank/team_detail.html', context)
