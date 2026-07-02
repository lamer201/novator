from django.shortcuts import get_list_or_404, get_object_or_404, render, redirect
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import *
from main.models import ItemProperty
from .models import Balance, Premia, Team, Zakaz, Material, ZakazItem, Status, Credit, CreditPayment, HistoryOperation
from mtr.models import Sklad, Stock, Shipment
from .func import check_active_credit, get_sum, check_balance, make_zakaz, make_zakaz_buildings, test_balance, make_zakaz_obuchenie, check_obuchenie, check_total_price
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
    elif request.GET.get('category') == 'kapremont':
        type_form = KapremontForm
    elif request.GET.get('category') == 'bank':
        type_form = ZakazFormBank
    else:
        messages.error(request, 'Неверная категория заказа.')
        return redirect('bank:bank_list')
    if request.method == 'POST':
        form = type_form(request.POST, user=request.user)
        if form.is_valid():
            if (get_sum(form) > Balance.objects.get(team=form.cleaned_data['team']).money):
                messages.error(request, 'Недостаточно средств на балансе для создания заказа.')
                return redirect('bank:bank_list')
            return make_zakaz(form)
    else:
        form = type_form(user=request.user)
    
    return render(request, 'bank/zakaz.html', {'form': form})

@login_required
def create_zakaz_team(request, team_id):
    if request.GET.get('category') == 'truba':
        type_form = ZakazFormTrubTeam
    elif request.GET.get('category') == 'auto':
        type_form = ZakazFormAutoTeam
    elif request.GET.get('category') == 'obuchenie':
        type_form = ZakazFormObuchenieTeam
    elif request.GET.get('category') == 'shtraf':
        type_form = ZakazFormShtrafTeam
    elif request.GET.get('category') == 'kapremont':
        type_form = KapremontFormTeam
    elif request.GET.get('category') == 'bank':
        type_form = ZakazFormBankTeam
    else:
        messages.error(request, 'Неверная категория заказа.')
        return redirect('bank:team_detail', team_id = team_id)
    if request.method == 'POST':
        form = type_form(request.POST)
        if form.is_valid():
            team = Team.objects.get(pk=form.cleaned_data['team'])
            if (get_sum(form) > Balance.objects.get(team=team).money):
                messages.error(request, 'Недостаточно средств на балансе для создания заказа.')
                return redirect('bank:team_detail', team_id = team_id)
            return make_zakaz(form)
    else:
        form = type_form(team_id = team_id)
        team_balance = Balance.objects.get(team__pk=team_id)
    
    return render(request, 'bank/zakaz.html', {'form': form,
                                               'balance': team_balance})


@login_required
def create_zakaz_buildings_team(request, team_id):
    if request.GET.get('category') == 'buildings':
        type_form = ZakazFormBuildingsTeam
    elif request.GET.get('category') == 'grs':
        type_form = ZakazFormGRSTeam
    elif request.GET.get('category') == 'ks':
        type_form = ZakazFormKSTeam
    else:
        messages.error(request, 'Неверная категория заказа.')
        return redirect('bank:team_detail', team_id = team_id)
    if request.method == 'POST':
        form = type_form(request.POST)
        if form.is_valid():
            return make_zakaz_buildings(form)
    else:
        form = type_form(team_id = team_id)
        team_balance = Balance.objects.get(team__pk=team_id)
    
    return render(request, 'bank/zakaz.html', {'form': form, 
                                               'balance': team_balance})

@login_required
def zakaz_check(request, zakaz_id):
    zakaz = Zakaz.objects.get(pk=zakaz_id)
    zakaz.status = Status.objects.get(pk=2)
    zakaz.save()
    return redirect('bank:zakaz_detail', zakaz_id=zakaz.pk)

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
        form = type_form(request.POST, user=request.user)
        if form.is_valid():
            return make_zakaz_buildings(form)
    else:
        form = type_form(user=request.user)
    
    return render(request, 'bank/zakaz.html', {'form': form})


@login_required
def create_zakaz_obuchenie(request):
    if request.method == 'POST':
        form = ZakazFormObuchenie(request.POST, user=request.user)
        if form.is_valid():
            if form.cleaned_data['learn_les'] == False and form.cleaned_data['learn_grs'] == False and form.cleaned_data['learn_ks'] == False:
                messages.error(request, 'Выберите хотя бы один вид обучения.')
                return redirect('bank:bank_list')
            return make_zakaz_obuchenie(form)
    else:
        form = ZakazFormObuchenie(user=request.user)
    
    return render(request, 'bank/zakaz.html', {'form': form})


@login_required
def create_zakaz_obuchenie_team(request, team_id):
    if request.method == 'POST':
        form = ZakazFormObuchenieTeam(request.POST)
        if form.is_valid():
            if form.cleaned_data['learn_les'] == False and form.cleaned_data['learn_grs'] == False and form.cleaned_data['learn_ks'] == False:
                messages.error(request, 'Выберите хотя бы один вид обучения.')
                return redirect('bank:team_detail', team_id = team_id)
            return make_zakaz_obuchenie(form)
    else:
        form = ZakazFormObuchenieTeam(team_id = team_id)
    
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
    """
    Add a material to an existing zakaz (order)
    """
    zakaz = get_object_or_404(Zakaz, pk=zakaz_id)
    
    # Check if request method is POST
    if request.method != 'POST':
        messages.error(request, 'Неверный метод запроса.')
        return redirect('bank:zakaz_detail', zakaz_id=zakaz.pk)

    # Get form data
    material_val = request.POST.get('material')
    qty_val = request.POST.get('quantity')
    koeff_val = request.POST.get('koeff', None)
    
    # Validate required fields
    if not material_val or not qty_val:
        messages.error(request, 'Материал и количество обязательны.')
        next_page = 'bank:zakaz_edit' if request.POST.get('next') == 'edit' else 'bank:zakaz_detail'
        return redirect(next_page, zakaz_id=zakaz.pk)
    
    # Validate quantity
    try:
        quantity = int(qty_val)
        if quantity <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        messages.error(request, 'Неверное количество.')
        return redirect('bank:zakaz_detail', zakaz_id=zakaz.pk)
    
    # Find material by pk or slug
    material = None
    try:
        material = Material.objects.get(pk=int(material_val))
    except (ValueError, TypeError):
        # If pk is not a valid integer, try to find by slug
        try:
            material = Material.objects.get(slug=material_val)
        except Material.DoesNotExist:
            material = None

    if material is None:
        messages.error(request, 'Материал не найден.')
        return redirect('bank:zakaz_detail', zakaz_id=zakaz.pk)

    # Validate and process coefficient
    try:
        koeff = float(koeff_val) if koeff_val is not None else 1.0
    except (ValueError, TypeError):
        koeff = 1.0

    # Calculate price and cost
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

    # Create the zakaz item
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
                history = HistoryOperation.objects.create(
                    team=zakaz.team,
                    operation_type='credit',
                    amount=total_refund,
                    balance_before=balance.money - total_refund,
                    balance_after=balance.money,
                    description= f'Возврат средств после удаления заказа {zakaz}'
                    )
                history.save()
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
@transaction.atomic
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
                history = HistoryOperation.objects.create(
                    team=zakaz.team,
                    operation_type='credit',
                    amount=total_refund,
                    balance_before=balance.money - total_refund,
                    balance_after=balance.money,
                    description= f'Возврат средств после отмены заказа {zakaz}'
                    )
                history.save()
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
@transaction.atomic
def zakaz_oplata(request, zakaz_id):
    zakaz = get_object_or_404(Zakaz, pk=zakaz_id)
    if zakaz.payment:
        messages.error(request, 'Заказ уже помечен как оплаченный.')
        return redirect('bank:zakaz_detail', zakaz_id=zakaz.pk)
    total_cost = sum(i.price * i.quantity for i in ZakazItem.objects.filter(zakaz=zakaz))
    balance = Balance.objects.get(team=zakaz.team)
    if zakaz.category.pk == 6:
        balance.money += total_cost
        history = HistoryOperation.objects.create(
            team=zakaz.team,
            operation_type='credit',
            amount=total_cost,
            balance_before=balance.money - total_cost,
            balance_after=balance.money,
            description= f'Получение премии за достижение {zakaz}'
        )
    else:
        if balance.money < total_cost:
            messages.error(request, 'Недостаточно средств на балансе для оплаты заказа.')
            return redirect('bank:zakaz_detail', zakaz_id=zakaz.pk)
        balance.money -= total_cost
        history = HistoryOperation.objects.create(
            team=zakaz.team,
            operation_type='debit',
            amount=total_cost,
            balance_before=balance.money + total_cost,
            balance_after=balance.money,
            description= f'Оплата заказа {zakaz}'
        )
    balance.save()
    
    history.save()
    zakaz.payment = True
    zakaz.status = Status.objects.get(name='Проверен банком')
    zakaz.save()

    messages.success(request, f'Заказ #{zakaz_id} успешно оплачен. Сумма {total_cost} списана с баланса.')
    return redirect('bank:bank_list')


@login_required
def zakaz_list(request):
    team_id = request.GET.get('team')
    if team_id:
        zakazy_qs = Zakaz.objects.filter(team=team_id).order_by('-id')
    else:
        zakazy_qs = Zakaz.objects.filter(team__name__in=request.user.userprofile.teams.values_list('name', flat=True)).order_by('-id')

    paginator = Paginator(zakazy_qs, 10)
    page = request.GET.get('page', 1)
    try:
        zakazy = paginator.page(page)
    except PageNotAnInteger:
        zakazy = paginator.page(1)
    except EmptyPage:
        zakazy = paginator.page(paginator.num_pages)

    zakaz_items = ZakazItem.objects.filter(zakaz__in=zakazy.object_list)
    return render(request, 'bank/zakaz_list.html', {
        'zakazy': zakazy,
        'zakaz_items': zakaz_items,
        'team': team_id,
    })

@login_required
def zakaz_detail(request, zakaz_id):
    zakaz = get_list_or_404(Zakaz, pk=zakaz_id)[0]
    items = ZakazItem.objects.filter(zakaz=zakaz)
    return render(request, 'bank/zakaz_detail.html', {'zakaz': zakaz, 'items': items})

@login_required
def bank_list(request):
    teams = Team.objects.filter(status=True, name__in=request.user.userprofile.teams.values_list('name', flat=True)).order_by('pk')
    
    list_teams = {}
    for team in teams:
        zakaz = Zakaz.objects.filter(team=team).count
        balance = Balance.objects.get(team=team)
        list_teams.update({team.pk: {'name': team.name, 'balance': balance.money, 'zakaz': zakaz}})
    new_zakaz = Zakaz.objects.filter(status=1, team__in=teams).order_by('-id')[:25]
    context = {
        'teams': list_teams,
        'new_zakazs': new_zakaz
    }
    return render(request, 'bank/bank.html', context)

@login_required
def team_detail(request, team_id):
    team = get_list_or_404(Team, pk=team_id)[0]
    balance = Balance.objects.get(team=team)
    zakazy = Zakaz.objects.filter(team=team).order_by('-id')
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
    credits = Credit.objects.filter(team=team)
    objects = ZakazItem.objects.filter(zakaz__team=team, material__category__slug='grs', zakaz__status__name='Завершен')
    history = HistoryOperation.objects.filter(team=team).order_by('-id')


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
        'credits': credits,
        'objects': objects,
        'history': history,
    }
    return render(request, 'bank/team_detail.html', context)

@login_required
@transaction.atomic
def zakaz_kapremont(request, team_id):
    if request.method == 'POST':
        data = request.POST
        if request.user.username == 'bank1':
            sklad = 'sklad-1'
        if request.user.username == 'bank2':
            sklad = 'sklad-2'
        else:
            sklad = 'sklad-3'
        team=Team.objects.get(pk=team_id)
        if not any(str(key).startswith('remove_') and value == 'on' for key, value in data.items()):
            messages.error(request, 'Вы не выбрали ни одного материала для списания. Пожалуйста, выберите хотя бы один материал и попробуйте снова.')
            return redirect('bank:zakaz_kapremont', team_id=team_id)
        for key, value in data.items():
            if str(key).startswith('remove_') and value == 'on':
                material_id = key.split('_')[1]
                stock_item = Stock.objects.get(pk=material_id)
                material_quantity = data.get(f'remove_count_{material_id}', 0)
                material_mtr = Material.objects.get(pk=stock_item.material.pk)
                shipment = Shipment(
                    from_warehouse=stock_item.warehouse,
                    to_warehouse=Sklad.objects.get(slug=sklad),
                    material=material_mtr,
                    quantity=material_quantity,
                    description=f'Возврат материала "{material_mtr.name}" от команды "{stock_item.warehouse.team.name}" при списании'
                )
                team.eco_scores.score += 5 * int(material_quantity)
                team.eco_scores.save()
                messages.info(request, f'Запрос на удаление материала ID {material_id} в количестве {material_quantity} получен.')
                try:
                    #material = Material.objects.get(pk=stock_item.material.pk)
                    if stock_item.quantity >= int(material_quantity):
                        shipment.perform_shipment()
                        messages.success(request, f'Материал "{material_mtr.name}" в количестве {material_quantity} успешно удалён со склада команды и возвращён на склад.')
                        return redirect('bank:zakaz_kapremont', team_id=team_id)
                    else:                        
                        messages.error(request, f'Недостаточно материала "{stock_item.material.name}" на складе для удаления.')
                        return redirect('bank:zakaz_kapremont', team_id=team_id)
                except (Material.DoesNotExist, Stock.DoesNotExist):
                    messages.error(request, 'Материал не найден на складе. Пожалуйста, проверьте данные и попробуйте снова.')
                    return redirect('bank:zakaz_kapremont', team_id=team_id)
        return redirect('bank:zakaz_kapremont', team_id=team_id)
    team = get_object_or_404(Team, pk=team_id)
    balance = Balance.objects.get(team=team)
    items = ZakazItem.objects.filter(zakaz__status__name='Выдан снабженцем', zakaz__team=team)
    materials = Stock.objects.filter(warehouse__team=team, quantity__gt=0, material__category__pk=1)
    return render(request, 'bank/zakaz_kapremont.html', {'team': team, 'items': items, 'materials': materials, 'balance': balance})

@login_required
def credit_list(request):
    credits = Credit.objects.all()
    return render(request, 'bank/credit_list.html', {'credits': credits})

@login_required
def credit_detail(request, credit_id):
    credit = get_object_or_404(Credit, pk=credit_id)
    balance = Balance.objects.get(team=credit.team)
    payments = CreditPayment.objects.filter(credit=credit)
    return render(request, 'bank/credit_detail.html', {'credit': credit, 'payments': payments, 'balance': balance})

@login_required
@transaction.atomic
def zakaz_credit(request):
    if request.method == 'POST':
        form = ZakazFormCredit(request.POST, user=request.user)
        if form.is_valid():
            team = Team.objects.get(pk=form.cleaned_data['team'])
        else:
            messages.error(request, 'Форма заполнена неверно. Пожалуйста, проверьте введённые данные.')
            return redirect('bank:new_credit')
        #if check_active_credit(request, team.pk):
        #    messages.error(request, 'У вашей команды уже есть активный кредит. Пожалуйста, погасите его перед оформлением нового кредита.')
        #    return redirect('bank:new_credit')
        balance = Balance.objects.get(team=team)
        if balance.money < 1000000:
            amount_val = 1000000
        else:
            amount_val = form.cleaned_data['amount']
        percent = request.POST.get('percent', 35)  # Default interest rate if not provided
        try:
            amount = float(amount_val)
            if amount <= 0:
                raise ValueError()
            if balance.money < amount and balance.money >= 1000000:
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
        history = HistoryOperation.objects.create(
            team=team,
            operation_type='credit',
            amount=amount,
            balance_before=balance.money - amount,
            balance_after=balance.money,
            description= f'Получение кредита на сумму {amount}'
            )
        history.save()
        messages.success(request, f'Кредит на сумму {amount} создан для команды "{team.name}".')
        return redirect('bank:credit_detail', credit_id=credit.pk)
    form = ZakazFormCredit(user=request.user)
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
        history = HistoryOperation.objects.create(
                team=credit.team,
                operation_type='debit',
                amount=payment_amount,
                balance_before=balance.money + payment_amount,
                balance_after=balance.money,
                description= f'Платеж по кредиту {credit.pk}'
                )
        history.save()

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
        form = PremiaForm(request.POST, user=request.user)
        if form.is_valid():
            team = Team.objects.get(pk=form.cleaned_data['team'])
            amount_val = form.cleaned_data['amount']
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
        history = HistoryOperation.objects.create(
                team=team,
                operation_type='credit',
                amount=amount,
                balance_before=balance.money - amount,
                balance_after=balance.money,
                description= f'Получение премии на сумму {amount}'
                )
        history.save()
        premia = Premia.objects.create(
            team=team,
            amount=amount,
            year=config.YEAR
        )
        premia.save()
        messages.success(request, f'Премия в размере {amount} добавлена на баланс команды "{team.name}".')
        return redirect('bank:new_premia')
    form = PremiaForm(user=request.user)
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

