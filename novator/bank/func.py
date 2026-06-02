from django.shortcuts import get_list_or_404, get_object_or_404, render, redirect
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .models import Balance, Credit, Team, Zakaz, Material, ZakazItem, Status
from main.models import Category, ItemProperty
from mtr.models import Stock
from main.models import ItemProperty
from constance import config

def get_sum(form):
    sum_material=0
    koeff = float(form.cleaned_data['koeff'])
    for field, quantity in form.cleaned_data.items():
        if field != 'team' and field != 'koeff' and quantity and field != 'category':
                    material = get_list_or_404(Material, slug=field)[0]
                    price = material.price*koeff
                    sum_material = sum_material + (price*quantity)
    return sum_material


def test_balance(price, balance):
    if price < balance:
        return True
    else:
        return False

def check_balance(request, team_id):
    try:
        item = Balance.objects.get(team=team_id)
        # Возвращаем нужное поле в JSON
        return JsonResponse({'text': item.money})
    except Balance.DoesNotExist:
        return JsonResponse({'text': ''}, status=404)

def check_obuchenie(request, team_id):
    team = Team.objects.get(id=team_id)
    learn_ks = team.learn_ks
    learn_grs = team.learn_grs
    learn_les = team.learn_les
    return JsonResponse({'learn_ks': learn_ks, 'learn_grs': learn_grs, 'learn_les': learn_les})


def check_active_credit(request, team_id):
    team = Team.objects.get(id=team_id)
    active_credit = Credit.objects.filter(team=team, status='active').exists()
    return active_credit

def make_zakaz(form):
    # Get form data
    team = Team.objects.get(pk=form.cleaned_data['team']) 
    balance = Balance.objects.get(team=team)     
    test_balance = get_sum(form)
    if test_balance > balance.money:
            message = f'Недостаточно средств на балансе для оплаты заказа. Необходимо {test_balance}, а на балансе {balance.money}.'
            return JsonResponse({'error': message}, status=400)
    else:        payment=True
    # Create new order
    zakaz = Zakaz.objects.create(
        team=team,
        year = config.YEAR,  # Use the value from Constance
        month = 0,
        payment=payment,
        status=Status.objects.get(name='Создан'),
        category = Category.objects.get(slug=form.cleaned_data['category'])
    )
    zakaz.save()
            
    for field, quantity in form.cleaned_data.items():
        if field != 'team' and field != 'koeff' and quantity and field != 'category':
            material = get_list_or_404(Material, slug=field)[0]
            koeff = float(form.cleaned_data['koeff'])
            price = material.price * koeff
            if material.category.slug == 'buildings':
                profit = ItemProperty.objects.get(material=material, property_name='cost').property_value
            else:
                profit = 0
            zakazItem = ZakazItem.objects.create(
                zakaz=zakaz,
                material=material,
                price=price,
                quantity=quantity,
                koeff=koeff,
                profit_val=profit
            )
            zakazItem.save()
        
    new_balance = balance.money - test_balance
    balance.money = new_balance
    balance.save()
    return redirect('bank:zakaz_detail', zakaz_id=zakaz.pk)  # Replace with your success URL


def make_zakaz_buildings(form):
    # Get form data
    team = Team.objects.get(pk=form.cleaned_data['team']) 
    balance = Balance.objects.get(team=team)    
    building = Material.objects.get(pk=form.cleaned_data['building']) 
    price = building.price * float(form.cleaned_data['koeff'])
    if building.category.slug == 'grs':
        profit = ItemProperty.objects.get(material=building, property_name='cost').property_value
    else:        profit = 0
    if test_balance(price, balance.money):
            payment=True
    else:        payment=False
            
    # Create new order
    zakaz = Zakaz.objects.create(
        team=team,
        year = config.YEAR,  # Use the value from Constance
        month = 0,
        payment=payment,
        status=Status.objects.get(name='Создан'),
        description=form.cleaned_data['description'],
        category=Category.objects.get(slug=form.cleaned_data['category'])
    )
    zakaz.save()

    zakazItem = ZakazItem.objects.create(
        zakaz=zakaz,
        material=building,
        price=price,
        quantity=1,  # Assuming quantity is always 1 for GRS items
        koeff=float(form.cleaned_data['koeff']) ,
        profit_val=profit
            )
    zakazItem.save()
        
    new_balance = balance.money - price
    balance.money = new_balance
    balance.save()
    return redirect('bank:zakaz_detail', zakaz_id=zakaz.pk)  # Replace with your success URL


def make_zakaz_obuchenie(form):
    team = Team.objects.get(pk=form.cleaned_data['team']) 
    balance = Balance.objects.get(team=team)
    koeff = float(form.cleaned_data['koeff'])
    if form.cleaned_data['learn_les']:         
        learn_les = Material.objects.get(slug='learn_les')
        price_les = learn_les.price * koeff
    else: 
        price_les = 0
        learn_les = None
    if form.cleaned_data['learn_grs']:         
        learn_grs = Material.objects.get(slug='learn_grs')
        price_grs = learn_grs.price * koeff
    else: 
        price_grs = 0
        learn_grs = None
    if form.cleaned_data['learn_ks']:         
        learn_ks = Material.objects.get(slug='learn_ks')
        price_ks = learn_ks.price * koeff
    else: 
        price_ks = 0
        learn_ks = None
    total_price = price_les + price_grs + price_ks
    if test_balance(total_price, balance.money):
            payment=True
    else:
         message = f'Недостаточно средств на балансе для оплаты обучения. Необходимо {total_price}, а на балансе {balance.money}.'
         return JsonResponse({'error': message}, status=400)
         
    # Create new order
    zakaz = Zakaz.objects.create(
        team=team,
        year = config.YEAR,  # Use the value from Constance
        month = 0,
        payment=payment,
        status=Status.objects.get(name='Создан'),
        description='Обучение',
        category = Category.objects.get(slug='learning')
    )
    zakaz.save()

    if learn_les:
        zakazItemLes = ZakazItem.objects.create(
            zakaz=zakaz,
            material=learn_les,  # No specific material for training
            price=price_les,
            quantity=1,
            koeff=koeff,
            profit_val=0
        )
        zakazItemLes.save()
    
    if learn_grs:
        zakazItemGrs = ZakazItem.objects.create(
            zakaz=zakaz,
            material=learn_grs,  # No specific material for training
            price=price_grs,
            quantity=1,
            koeff=koeff,
            profit_val=0
        )
        zakazItemGrs.save()
    
    if learn_ks:
        zakazItemKs = ZakazItem.objects.create(
            zakaz=zakaz,
            material=learn_ks,  # No specific material for training
            price=price_ks,
            quantity=1,
            koeff=koeff,
            profit_val=0
        )
        zakazItemKs.save()
        
    new_balance = balance.money - total_price
    balance.money = new_balance
    balance.save()
    zakaz.status = Status.objects.get(name='Проверен банком')
    zakaz.save()
    return redirect('bank:zakaz_detail', zakaz_id=zakaz.pk)

def give_money(team):
    balance = Balance.objects.get(team=team)
    balance.money += config.MONEY_PER_YEAR
    for grs in ZakazItem.objects.filter(zakaz__team=team, material__category__slug='grs'):
        balance.money += grs.calculate_profit
    balance.save()
    return JsonResponse({'text': balance.money})