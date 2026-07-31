from django.shortcuts import get_list_or_404, get_object_or_404, render, redirect
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .models import Balance, Credit, Team, Zakaz, Material, ZakazItem, Status, HistoryOperation, CreditPayment
from main.models import Category, ItemProperty
from mtr.models import Stock
from main.models import ItemProperty
from constance import config
from django.db import transaction
from django.db.models import Q


def get_sum(form):
    sum_material=0
    koeff = float(form.cleaned_data['koeff'])
    for field, quantity in form.cleaned_data.items():
        if field != 'team' and field != 'koeff' and quantity and field != 'category':
                    material = get_list_or_404(Material, slug=field)[0]
                    price = material.price*koeff
                    sum_material = sum_material + (price*quantity)
    return sum_material

def history(**kwargs):
    zakaz = kwargs.get('zakaz', None)
    price = kwargs.get('price', None)
    balance = kwargs.get('balance', None)
    description = kwargs.get('description', None)
    if zakaz is None:
        team = kwargs.get('team', None)
    else:
        team = zakaz.team
    operation_type = kwargs.get('operation_type', None)
    if operation_type == 'debit':
        balance_before = balance.money + price
    elif operation_type == 'credit':
        balance_before = balance.money - price
    make_history = HistoryOperation.objects.create(
        team=team,
        operation_type=operation_type,
        amount=price,
        balance_before=balance_before,
        balance_after=balance.money,
        description= description
        )
    make_history.save()


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


def check_total_price(request, material_id, quantity):
    try:
        item = Material.objects.get(id=material_id)
        total_price = item.price * float(quantity)
        # Возвращаем нужное поле в JSON
        return JsonResponse({'total_price': total_price})
    except Material.DoesNotExist:
        return JsonResponse({'total_price': ''}, status=404)


""" def compute_total_price_from_data(data):
    koeff = 1.0
    try:
        koeff = float(data.get('koeff') or 1.0)
    except (TypeError, ValueError):
        koeff = 1.0

    total_price = 0.0

    material_id = data.get('material')
    if material_id:
        try:
            material = Material.objects.get(pk=int(material_id))
            quantity = float(data.get('quantity') or 1)
            total_price += material.price * koeff * quantity
        except (Material.DoesNotExist, ValueError, TypeError):
            pass

    for field, value in data.items():
        if field in ('team', 'koeff', 'category', 'material', 'team_balance', 'csrfmiddlewaretoken'):
            continue

        if field in ('learn_les', 'learn_grs', 'learn_ks'):
            if value in ('on', 'true', 'True', '1', True):
                try:
                    material = Material.objects.get(slug=field)
                    total_price += material.price * koeff
                except Material.DoesNotExist:
                    pass
            continue

        try:
            quantity = float(value)
        except (TypeError, ValueError):
            continue

        if quantity <= 0:
            continue

        try:
            material = Material.objects.get(slug=field)
        except Material.DoesNotExist:
            continue

        total_price += material.price * koeff * quantity

    return total_price
 """

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

def make_zakaz_many_item(form):
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
    history(operation_type='debit', zakaz=zakaz, price=test_balance, balance=balance, description=f'Оплата заказа {zakaz.pk}')
    return redirect('bank:zakaz_detail', zakaz_id=zakaz.pk)  # Replace with your success URL

@transaction.atomic
def make_zakaz_one_item(form):
    # Get form data
    team = Team.objects.get(pk=form.cleaned_data['team']) 
    balance = Balance.objects.get(team=team)    
    material = Material.objects.get(pk=form.cleaned_data['material']) 
    price = material.price * float(form.cleaned_data['koeff'])
    if material.category.slug == 'grs':
        profit = ItemProperty.objects.get(material=material, property_name='cost').property_value
        nomer_dogovora = Zakaz.objects.filter(category__slug='grs',team=team).filter(~Q(status__name='Отменён')).count() +1
    else:        
         profit = 0
         nomer_dogovora=''       
    if test_balance(price, balance.money):
            payment=True
    else:
        message = f'Недостаточно средств на балансе для оплаты заказа. Необходимо {price}, а на балансе {balance.money}.'
        return JsonResponse({'error': message}, status=400)  
    # Create new order
    if material.slug == 'spg':
        status = Status.objects.get(pk=2)
    else:
        status = Status.objects.get(pk=1)
    zakaz = Zakaz.objects.create(
        team=team,
        year = config.YEAR,  # Use the value from Constance
        month = 0,
        payment=payment,
        status=status,
        description=nomer_dogovora,
        category=Category.objects.get(slug=form.cleaned_data['category'])
    )
    zakaz.save()

    zakazItem = ZakazItem.objects.create(
        zakaz=zakaz,
        material=material,
        price=price,
        quantity=1,  # Assuming quantity is always 1 for GRS items
        koeff=float(form.cleaned_data['koeff']) ,
        profit_val=profit
            )
    zakazItem.save()
        
    new_balance = balance.money - price
    balance.money = new_balance
    balance.save()
    history(operation_type='debit', zakaz=zakaz, price=price, balance=balance, description=f'Оплата заказа {zakaz.pk}')
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
    if learn_les:
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
        zakaz.status = Status.objects.get(name='Проверен банком')
        zakaz.save()
        zakazItemLes = ZakazItem.objects.create(
            zakaz=zakaz,
            material=learn_les,  # No specific material for training
            price=price_les,
            quantity=1,
            koeff=koeff,
            profit_val=0
        )
        zakazItemLes.save()
        history(operation_type='debit', zakaz=zakaz, price=price_les, balance=balance, description=f'Оплата заказа {zakaz.pk}')
    if learn_grs:
        zakaz = Zakaz.objects.create(
            team=team,
            year = config.YEAR,  # Use the value from Constance
            month = 0,
            payment=payment,
            status=Status.objects.get(name='Создан'),
            description='Обучение',
            category = Category.objects.get(slug='learning')
        )
        zakaz.status = Status.objects.get(name='Проверен банком')
        zakaz.save()
        zakazItemGrs = ZakazItem.objects.create(
            zakaz=zakaz,
            material=learn_grs,  # No specific material for training
            price=price_grs,
            quantity=1,
            koeff=koeff,
            profit_val=0
        )
        zakazItemGrs.save()
        history(operation_type='debit', zakaz=zakaz, price=price_grs, balance=balance, description=f'Оплата заказа {zakaz.pk}')
    
    if learn_ks:
        zakaz = Zakaz.objects.create(
            team=team,
            year = config.YEAR,  # Use the value from Constance
            month = 0,
            payment=payment,
            status=Status.objects.get(name='Создан'),
            description='Обучение',
            category = Category.objects.get(slug='learning')
        )
        zakaz.status = Status.objects.get(name='Проверен банком')
        zakaz.save()
        zakazItemKs = ZakazItem.objects.create(
            zakaz=zakaz,
            material=learn_ks,  # No specific material for training
            price=price_ks,
            quantity=1,
            koeff=koeff,
            profit_val=0
        )
        zakazItemKs.save()
        history(operation_type='debit', zakaz=zakaz, price=price_ks, balance=balance, description=f'Оплата заказа {zakaz.pk}')
        
    new_balance = balance.money - total_price
    balance.money = new_balance
    balance.save()
    return redirect('bank:zakaz_detail', zakaz_id=zakaz.pk)

def give_money(team):
    balance = Balance.objects.get(team=team)
    balance.money += config.MONEY_PER_YEAR
    history(operation_type='credit', team=team, price=config.MONEY_PER_YEAR, balance=balance, description=f'Ежегодная премия {config.MONEY_PER_YEAR}')
    for grs in ZakazItem.objects.filter(zakaz__team=team, material__category__slug='grs'):
        balance.money += grs.calculate_profit
        history(operation_type='credit', team=team, price=grs.calculate_profit, balance=balance, grs=grs, description=f'Прибыль от {grs.material.name}')
    balance.save()
    return JsonResponse({'text': balance.money})


def calculate_win_score(team):
    balance = Balance.objects.get(team=team)
    grs_money = 0
    grs_potrebiteli = 0
    bonus_score = 0
    for grs in ZakazItem.objects.filter(zakaz__team=team, material__category__slug='grs', zakaz__status__pk=5):
        grs_money += grs.calculate_profit
        grs_potrebiteli += float(ItemProperty.objects.get(material=grs.material, property_name='potrebitel').property_value)
    total_money = balance.money 
    if ZakazItem.objects.filter(zakaz__team=team, material__category__slug='premii').exists():
         for item in ZakazItem.objects.filter(zakaz__team=team, material__category__slug='premii'):
            bonus_score += float(ItemProperty.objects.get(material=item.material, property_name='winner_score').property_value)

    total_points = (grs_potrebiteli * 0.001) + (total_money * 0.000001) + (team.eco_scores.score * 0.05) + bonus_score
    return total_points
    

def end_game(team):
    balance = Balance.objects.get(team=team)
    for grs in ZakazItem.objects.filter(zakaz__team=team, material__category__slug='grs'):
        balance.money += grs.calculate_profit
        history(operation_type='credit', team=team, price=grs.calculate_profit, balance=balance, grs=grs, description=f'Прибыль от {grs.material.name}')
    if Credit.objects.filter(team=team, status='active').exists():
         credits = Credit.objects.filter(team=team, status='active')
         for credit in credits:
            payment = CreditPayment.objects.create(
              credit=credit,
              amount=credit.remains,
              year=config.YEAR
            )
            payment.save()
            balance.money-=credit.remains
            credit.status='paid'
            history(operation_type='debit', team=team, price=credit.remains, balance=balance, credit=credit, description=f'Выплата кредита {credit.pk}')
            credit.save()
    if not Zakaz.objects.filter(team=team, category__slug='shtrafs', status__pk=5).exists():
        material = Material.objects.get(slug='bez_suchka')
        zakaz=Zakaz.objects.create(
            team=team,
            year = config.YEAR,
            month = 0,
            payment = True,
            category = Category.objects.get(slug='premii'),
            status = Status.objects.get(name='Завершен')
        )
        ZakazItem.objects.create(
            zakaz=zakaz,
            material = material,
            price = material.price,
            quantity = 1,
            koeff = 1,
            profit_val = ItemProperty.objects.get(material=material, property_name='winner_score').property_value
            
        )
        balance.money += material.price
        history(operation_type='credit', zakaz=zakaz, price=material.price, balance=balance, description=f'Прибыль от премии {material.name}')
    balance.save()
    return JsonResponse({'text': balance.money})