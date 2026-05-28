from django.shortcuts import get_list_or_404, get_object_or_404, render, redirect
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import transaction
from .forms import *
from main.models import ItemProperty
from .models import Balance, Premia, Team, Zakaz, Material, ZakazItem, Status, Credit, CreditPayment
from mtr.models import Sklad, Stock, Shipment
from .func import get_sum, check_balance, make_zakaz, make_zakaz_buildings, test_balance, make_zakaz_obuchenie
from constance import config

User = get_user_model()

@login_required
def zakaz_issued(request, zakaz_id):
    zakaz = get_object_or_404(Zakaz, pk=zakaz_id)
    zakaz.issued = True
    zakaz.status = Status.objects.get(pk=3)  # Assuming pk=3 corresponds to "Выдан"
    zakaz.save()
    return redirect('mtr:index')

@login_required
def create_zakaz(request):
    if request.GET.get('category') == 'auto':
        type_form = ZakazFormAuto
    elif request.GET.get('category') == 'obuchenie':
        type_form = ZakazFormObuchenie
    elif request.GET.get('category') == 'shtraf':
        type_form = ZakazFormShtraf
    elif request.GET.get('category') == 'truba':
        type_form = ZakazFormTrub
    else:
        messages.error(request, 'Неверная категория заказа.')
        return redirect('bank:bank_list')
    if request.method == 'POST':
        form = type_form(request.POST)
        if form.is_valid():
            if (get_sum(form) > Balance.objects.get(team=form.cleaned_data['team']).money):
                messages.error(request, 'Недостаточно средств на балансе для создания заказа.')
                return redirect('bank:bank_list')
            return make_zakaz(form)
    else:
        form = type_form()
    
    return render(request, 'bank/zakaz.html', {'form': form})


@login_required
def create_zakaz_buildings(request):
    if request.GET.get('category') == 'buildings':
        type_form = ZakazFormBuildings
    elif request.GET.get('category') == 'grs':
        type_form = ZakazFormGRS
    elif request.GET.get('category') == 'ks':
        type_form = ZakazFormKS
    else:
        messages.error(request, 'Неверная категория заказа.')
        return redirect('bank:bank_list')
    if request.method == 'POST':
        form = type_form(request.POST)
        if form.is_valid():
            return make_zakaz_buildings(form)
    else:
        form = type_form()
    
    return render(request, 'bank/zakaz.html', {'form': form})


@login_required
def create_zakaz_obuchenie(request):
    if request.method == 'POST':
        form = ZakazFormObuchenie(request.POST)
        if form.is_valid():
            if form.cleaned_data['learn_les'] == False and form.cleaned_data['learn_grs'] == False and form.cleaned_data['learn_ks'] == False:
                messages.error(request, 'Выберите хотя бы один вид обучения.')
                return redirect('bank:bank_list')
            return make_zakaz_obuchenie(form)
    else:
        form = ZakazFormObuchenie()
    
    return render(request, 'bank/zakaz.html', {'form': form})

@login_required
def zakaz_edit(request, zakaz_id):
    zakaz = get_object_or_404(Zakaz, pk=zakaz_id)
    items = ZakazItem.objects.filter(zakaz=zakaz)
    materials = Material.objects.all()

    if request.method == 'POST':
        # preserve original totals for balance adjustments
        orig_items = list(items)
        orig_total = sum(i.price * i.quantity for i in orig_items)

        # Update item fields from POST (expecting price_<id> and qty_<id>)
        for item in items:
            price_val = request.POST.get(f'price_{item.pk}')
            qty_val = request.POST.get(f'qty_{item.pk}')
            try:
                if price_val is not None:
                    item.price = float(price_val)
                if qty_val is not None:
                    item.quantity = int(qty_val)
                item.save()
            except (ValueError, TypeError):
                messages.error(request, 'Неверные значения цены или количества для позиции.')
                return render(request, 'bank/zakaz_edit.html', {'zakaz': zakaz, 'items': items, 'statuses': Status.objects.all()})

        # Recalculate totals
        new_items = ZakazItem.objects.filter(zakaz=zakaz)
        new_total = sum(i.price * i.quantity for i in new_items)

        # Payment and issued flags
        payment_checked = True if request.POST.get('payment') == 'on' else False
        issued_checked = True if request.POST.get('issued') == 'on' else False

        # Status change
        status_id = request.POST.get('status')
        if status_id:
            try:
                zakaz.status = Status.objects.get(pk=int(status_id))
            except Exception:
                pass

        # Adjust balance according to payment changes or total differences
        balance = Balance.objects.get(team=zakaz.team)

        # If payment state changed from unpaid -> paid
        if not zakaz.payment and payment_checked:
            if balance.money >= new_total:
                balance.money -= new_total
                zakaz.payment = True
            else:
                messages.error(request, 'Недостаточно средств на балансе для пометки заказа как оплачен.')
                return render(request, 'bank/zakaz_edit.html', {'zakaz': zakaz, 'items': new_items, 'statuses': Status.objects.all()})

        # If payment state changed from paid -> unpaid (refund original amount)
        elif zakaz.payment and not payment_checked:
            balance.money += orig_total
            zakaz.payment = False

        # If payment remained True but totals changed, adjust by delta
        elif zakaz.payment and payment_checked:
            delta = new_total - orig_total
            if delta > 0 and balance.money < delta:
                messages.error(request, 'Недостаточно средств для увеличения оплаченной суммы заказа.')
                return render(request, 'bank/zakaz_edit.html', {'zakaz': zakaz, 'items': new_items, 'statuses': Status.objects.all()})
            balance.money -= delta

        balance.save()

        zakaz.issued = issued_checked
        zakaz.save()

        #messages.success(request, 'Заказ успешно обновлён.')
        return redirect('bank:zakaz_detail', zakaz_id=zakaz.pk)

    # GET
    return render(request, 'bank/zakaz_edit.html', {'zakaz': zakaz, 'items': items, 'statuses': Status.objects.all(), 'materials': materials})

@login_required
def zakaz_add_material(request, zakaz_id):
    zakaz = get_object_or_404(Zakaz, pk=zakaz_id)
    if request.method != 'POST':
        messages.error(request, 'Неверный метод запроса.')
        return redirect('bank:zakaz_detail', zakaz_id=zakaz.pk)

    material_val = request.POST.get('material')
    qty_val = request.POST.get('quantity')
    koeff_val = request.POST.get('koeff', None)

    if not material_val or not qty_val:
        messages.error(request, 'Материал и количество обязательны.')
        return redirect('bank:zakaz_edit' if request.POST.get('next') == 'edit' else 'bank:zakaz_detail', zakaz_id=zakaz.pk)

    try:
        quantity = int(qty_val)
        if quantity <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        messages.error(request, 'Неверное количество.')
        return redirect('bank:zakaz_detail', zakaz_id=zakaz.pk)

    # find material by pk or slug
    material = None
    try:
        material = Material.objects.get(pk=int(material_val))
    except Exception:
        try:
            material = Material.objects.get(slug=material_val)
        except Material.DoesNotExist:
            material = None

    if material is None:
        messages.error(request, 'Материал не найден.')
        return redirect('bank:zakaz_detail', zakaz_id=zakaz.pk)

    try:
        koeff = float(koeff_val) if koeff_val is not None else 1.0
    except (ValueError, TypeError):
        koeff = 1.0

    price = material.price * koeff
    cost = price * quantity

    # If zakaz already marked paid, charge the team's balance for the added item
    if zakaz.payment:
        try:
            balance = Balance.objects.get(team=zakaz.team)
        except Balance.DoesNotExist:
            messages.error(request, 'Баланс команды не найден. Добавление отменено.')
            return redirect('bank:zakaz_detail', zakaz_id=zakaz.pk)

        if balance.money < cost:
            messages.error(request, 'Недостаточно средств на балансе для добавления материала к оплаченному заказу.')
            return redirect('bank:zakaz_detail', zakaz_id=zakaz.pk)

        balance.money -= cost
        balance.save()

    # create item
    ZakazItem.objects.create(
        zakaz=zakaz,
        material=material,
        price=price,
        quantity=quantity,
        koeff=koeff
    )

    messages.success(request, f'Материал "{material.name}" добавлен в заказ #{zakaz.pk}.')
    return redirect('bank:zakaz_detail', zakaz_id=zakaz.pk)

@login_required
def zakaz_delete(request, zakaz_id):
    zakaz = get_object_or_404(Zakaz, pk=zakaz_id)
    if request.method == 'POST':
        items = ZakazItem.objects.filter(zakaz=zakaz)
        total_refund = sum(i.price * i.quantity for i in items)

        if zakaz.payment:
            try:
                balance = Balance.objects.get(team=zakaz.team)
                balance.money += total_refund
                balance.save()
            except Balance.DoesNotExist:
                messages.error(request, 'Баланс команды не найден. Удаление отменено.')
                return redirect('bank:zakaz_detail', zakaz_id=zakaz.pk)

        zakaz.delete()
        if zakaz.payment:
            messages.success(request, f'Заказ #{zakaz_id} удалён и сумма {total_refund} возвращена на баланс.')
        else:
            messages.success(request, f'Заказ #{zakaz_id} удалён.')
        return redirect('bank:zakaz_list')

    return render(request, 'bank/zakaz_confirm_delete.html', {'zakaz': zakaz})

@login_required
def zakaz_otmena(request, zakaz_id):
    zakaz = get_object_or_404(Zakaz, pk=zakaz_id)
    if request.method == 'POST':
        items = ZakazItem.objects.filter(zakaz=zakaz)
        total_refund = sum(i.price * i.quantity for i in items)

        if zakaz.payment:
            try:
                balance = Balance.objects.get(team=zakaz.team)
                balance.money += total_refund
                balance.save()
            except Balance.DoesNotExist:
                messages.error(request, 'Баланс команды не найден. Отмена заказа отменена.')
                return redirect('bank:zakaz_detail', zakaz_id=zakaz.pk)

        zakaz.status = Status.objects.get(name='Отменён')
        zakaz.save()
        if zakaz.payment:
            messages.success(request, f'Заказ #{zakaz_id} отменён и сумма {total_refund} возвращена на баланс.')
        else:
            messages.success(request, f'Заказ #{zakaz_id} отменён.')
        return redirect('bank:zakaz_list')

    return render(request, 'bank/zakaz_confirm_cancel.html', {'zakaz': zakaz})


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

@login_required
def bank_list(request):
    teams = Team.objects.filter(status=True)
    
    list_teams = {}
    for team in teams:
        zakaz = Zakaz.objects.filter(team=team).count
        balance = Balance.objects.get(team=team)
        list_teams.update({team.pk: {'name': team.name, 'balance': balance.money, 'zakaz': zakaz}})
    new_zakaz = Zakaz.objects.filter(status=1)
    context = {
        'teams': list_teams,
        'new_zakazs': new_zakaz
    }
    return render(request, 'bank/bank.html', context)

@login_required
def team_detail(request, team_id):
    team = get_list_or_404(Team, pk=team_id)[0]
    balance = Balance.objects.get(team=team)
    zakazy = Zakaz.objects.filter(team=team)
    obuchenie = type('Obuchenie', (), {})()
    transport = zakazy.filter(zakazitem__material__category__slug='auto').count()
    truba = zakazy.filter(zakazitem__material__category__slug='trubi').count() * 20
    obuchenie.lin = team.learn_les
    obuchenie.grs = team.learn_grs
    obuchenie.ks =  team.learn_ks
    zakazy_lin = zakazy.filter(zakazitem__material__category__slug='trubi').count()
    zakazy_grs = zakazy.filter(zakazitem__material__category__slug='grs').count()
    zakazy_ks = zakazy.filter(zakazitem__material__category__slug='ks').count()
    zakazy_shtraf = zakazy.filter(zakazitem__material__category__slug='shtrafs').count()
    objects = ZakazItem.objects.filter(zakaz__team=team, material__category__slug='grs', zakaz__status__name='Выдан снабженцем')


    context = {
        'team': team,
        'balance': balance.money,
        'zakazy': zakazy,
        'obuchenie': obuchenie,
        'transport': transport,
        'truba': truba,
        'zakazy_lin': zakazy_lin,
        'zakazy_grs': zakazy_grs,
        'zakazy_ks': zakazy_ks,
        'zakazy_shtraf': zakazy_shtraf,
        'objects': objects,
    }
    return render(request, 'bank/team_detail.html', context)

@login_required
@transaction.atomic
def zakaz_kapremont(request, team_id):
    if request.method == 'POST':
        data = request.POST
        if not any(str(key).startswith('use_') and value == 'on' for key, value in data.items()) and not any(str(key).startswith('remove_') and value == 'on' for key, value in data.items()):
            messages.error(request, 'Вы не выбрали ни одного материала для добавления или удаления. Пожалуйста, выберите хотя бы один материал и попробуйте снова.')
            return redirect('bank:zakaz_kapremont', team_id=team_id)
        if any(str(key).startswith('use_') and value == 'on' for key, value in data.items()):
            zakaz= Zakaz.objects.create(
                            team=Team.objects.get(pk=team_id),
                            year=config.YEAR,
                            month=0,
                            payment=True,
                            status=Status.objects.get(name='Выдан снабженцем'),
                            description=f'Заказ на капитальный ремонт команды {Team.objects.get(pk=team_id).name}'
                        )
            zakaz.save()
        for key, value in data.items():
            if str(key).startswith('use_') and value == 'on':
                material_id = key.split('_')[1]
                stock_item = Stock.objects.get(pk=material_id)
                material = Material.objects.get(pk=stock_item.material.pk)
                quantity = data.get(f'use_count_{material_id}', 0)
                try:
                    if int(quantity) <= 0:
                        messages.error(request, f'Неверное количество для материала "{material.name}". Пожалуйста, введите положительное целое число.')
                        return redirect('bank:zakaz_kapremont', team_id=team_id)    
                    if quantity:
                        zakaz_item = ZakazItem.objects.create(
                            zakaz=zakaz,
                            material=material,
                            price=material.price,
                            quantity=int(quantity),
                            koeff=0.5
                        )
                        zakaz_item.save()
                        messages.info(request, f'Материал "{material.name}" в количестве {quantity} добавлен в заказ № {zakaz.pk} на капитальный ремонт.')
                except (ValueError, TypeError):
                    messages.error(request, f'Неверное количество для материала "{material.name}". Пожалуйста, введите положительное целое число.')
                    return redirect('bank:zakaz_kapremont', team_id=team_id)
            if str(key).startswith('remove_') and value == 'on':
                material_id = key.split('_')[1]
                stock_item = Stock.objects.get(pk=material_id)
                material_quantity = data.get(f'remove_count_{material_id}', 0)
                material_mtr = Material.objects.get(pk=stock_item.material.pk)
                shipment = Shipment(
                    from_warehouse=stock_item.warehouse,
                    to_warehouse=Sklad.objects.get(slug='sklad-1'),
                    material=material_mtr,
                    quantity=material_quantity,
                    description=f'Возврат материала "{material_mtr.name}" от команды "{stock_item.warehouse.team.name}" при заказе на капремонт'
                )
                messages.info(request, f'Запрос на удаление материала ID {material_id} в количестве {material_quantity} получен.')
                try:
                    #material = Material.objects.get(pk=stock_item.material.pk)
                    if stock_item.quantity >= int(material_quantity):
                        shipment.perform_shipment()
                        messages.success(request, f'Материал "{material_mtr.name}" в количестве {material_quantity} успешно удалён из заказа на капремонт и возвращён на склад.')
                        return redirect('bank:zakaz_kapremont', team_id=team_id)
                    else:                        
                        messages.error(request, f'Недостаточно материала "{stock_item.material.name}" на складе для удаления.')
                        return redirect('bank:zakaz_kapremont', team_id=team_id)
                except (Material.DoesNotExist, Stock.DoesNotExist):
                    messages.error(request, 'Материал не найден на складе. Пожалуйста, проверьте данные и попробуйте снова.')
                    return redirect('bank:zakaz_kapremont', team_id=team_id)
                
        messages.success(request, 'Заказ на капитальный ремонт сохранён.')
        return redirect('bank:zakaz_kapremont', team_id=team_id)
    team = get_object_or_404(Team, pk=team_id)
    balance = Balance.objects.get(team=team)
    items = ZakazItem.objects.filter(zakaz__status__name='Выдан снабженцем', zakaz__team=team)
    materials = Stock.objects.filter(warehouse__team=team, quantity__gt=0, material__category__pk=1)
    zakaz_form = KapremontForm()
    return render(request, 'bank/zakaz_kapremont.html', {'team': team, 'items': items, 'materials': materials, 'balance': balance, 'form': zakaz_form})

@login_required
def credit_list(request):
    credits = Credit.objects.all()
    return render(request, 'bank/credit_list.html', {'credits': credits})

@login_required
def credit_detail(request, credit_id):
    credit = get_object_or_404(Credit, pk=credit_id)
    payments = CreditPayment.objects.filter(credit=credit)
    return render(request, 'bank/credit_detail.html', {'credit': credit, 'payments': payments})

@login_required
@transaction.atomic
def zakaz_credit(request):
    if request.method == 'POST':
        team = Team.objects.get(pk=request.POST.get('team'))
        amount_val = request.POST.get('amount')
        percent = request.POST.get('percent', 35)  # Default interest rate if not provided
        balance = Balance.objects.get(team=team)
        try:
            amount = float(amount_val)
            if amount <= 0:
                raise ValueError()
            if balance.money < amount:
                messages.error(request, 'Недостаточно средств на балансе для получения кредита. Требуется иметь на балансе сумму, равную запрашиваемому кредиту.')
                return redirect('bank:new_credit')
        except (ValueError, TypeError):
            messages.error(request, 'Неверная сумма кредита. Пожалуйста, введите положительное число.')
            return redirect('bank:new_credit')

        credit = Credit.objects.create(
            team=team,
            amount=amount,  # Total amount to be repaid including interest
            year=config.YEAR,
            percent=percent,
            remains=amount* (1 + (float(percent) / 100)),  # Initial remaining amount is the total amount to be repaid
            #remains_percent=amount * (int(percent) / 100)
        )
        credit.save()
        balance.money += amount
        balance.save()
        messages.success(request, f'Кредит на сумму {amount} создан для команды "{team.name}".')
        return redirect('bank:credit_detail', credit_id=credit.pk)
    form = ZakazFormCredit()
    return render(request, 'bank/zakaz_credit.html', {'form': form})

@login_required
@transaction.atomic
def make_payment(request, credit_id):
    credit = get_object_or_404(Credit, pk=credit_id)
    if request.method == 'POST':
        payment_amount_val = request.POST.get('payment_amount')
        balance = Balance.objects.get(team=credit.team)
        try:
            payment_amount = float(payment_amount_val)
            if payment_amount <= 0:
                raise ValueError()
            if balance.money < payment_amount:
                messages.error(request, 'Недостаточно средств на балансе для оплаты кредита. Пожалуйста, пополните баланс и попробуйте снова.')
                return redirect('bank:credit_detail', credit_id=credit.pk)
            if payment_amount > credit.remains:
                messages.error(request, 'Сумма платежа превышает оставшуюся сумму кредита. Пожалуйста, введите корректную сумму.')
                return redirect('bank:credit_detail', credit_id=credit.pk)
        except (ValueError, TypeError):
            messages.error(request, 'Неверная сумма платежа. Пожалуйста, введите положительное число.')
            return redirect('bank:credit_detail', credit_id=credit.pk)

        # Deduct payment from balance and update credit
        balance.money -= payment_amount
        balance.save()

        credit.remains -= payment_amount
        #credit.remains_percent -= payment_amount * (credit.percent / 100)
        credit.save()

        CreditPayment.objects.create(
            credit=credit,
            amount=payment_amount,
            year=config.YEAR
        )
        if credit.is_fully_paid():  
            credit.status = 'paid'
            credit.save()
        messages.success(request, f'Платеж в размере {payment_amount} успешно произведён по кредиту #{credit.pk}.')
        return redirect('bank:credit_detail', credit_id=credit.pk)
        

    return redirect('bank:credit_detail', credit_id=credit.pk)

@login_required
@transaction.atomic
def new_premia(request):
    if request.method == 'POST':
        team = Team.objects.get(pk=request.POST.get('team'))
        amount_val = request.POST.get('amount')
        balance = Balance.objects.get(team=team)
        try:
            amount = float(amount_val)
            if amount <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            messages.error(request, 'Неверная сумма премии. Пожалуйста, введите положительное число.')
            return redirect('bank:new_premia')

        balance.money += amount
        balance.save()
        premia = Premia.objects.create(
            team=team,
            amount=amount,
            year=config.YEAR
        )
        premia.save()
        messages.success(request, f'Премия в размере {amount} добавлена на баланс команды "{team.name}".')
        return redirect('bank:new_premia')
    form = PremiaForm()
    teams = Team.objects.filter(status=True)
    premii = Premia.objects.all()
    return render(request, 'bank/new_premia.html', {'form': form, 'teams': teams, 'premii': premii})

@login_required
@require_POST
def zapusk_edit(request):
    if request.method == 'POST':
        zakaz_item_id = request.POST.get('zakaz_item')
        profit_koeff = request.POST.get('koeff_val')
        zakaz_item = get_object_or_404(ZakazItem, pk=zakaz_item_id)
        try:
            if profit_koeff is not None:
                zakaz_item.profit_koeff = float(profit_koeff)
            zakaz_item.save()
            messages.success(request, 'Позиция успешно обновлена.')
        except (ValueError, TypeError):
            messages.error(request, 'Неверные значения коэффициента прибыли. Пожалуйста, введите корректные данные.')
    return redirect('bank:team_detail', team_id=zakaz_item.zakaz.team.pk)
