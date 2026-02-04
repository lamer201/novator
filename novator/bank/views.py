from django.shortcuts import get_list_or_404, render, redirect, HttpResponseRedirect, HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .froms import ZakazForm1
from .models import Balance, Buy, Team, Zakaz, Material, ZakazItem

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


@login_required
def create_zakaz(request):
    if request.method == 'POST':
        form = ZakazForm1(request.POST)
        if form.is_valid():
            # Get form data
            team = Team.objects.get(pk=form.cleaned_data['team']) 
            balance = Balance.objects.get(team=team)           
            test_balance = get_sum(form, balance)
            if test_balance == 0:
                 payment=False
            
            # Create new order
            zakaz = Zakaz.objects.create(
                team=team,
                year = 1,
                month = 0,
                payment=True
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
    else:
        form = ZakazForm1()
    
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
