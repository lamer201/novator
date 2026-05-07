from django.shortcuts import get_list_or_404, get_object_or_404, render, redirect
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ZakazFormAuto, ZakazFormObuchenie, ZakazFormShtraf, ZakazFormTrub, ZakazFormKSGRS
from .models import Balance, Buy, Team, Zakaz, Material, ZakazItem, Status
from mtr.models import Sklad, Stock
from .func import get_sum, check_balance, make_zakaz

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
    elif request.GET.get('category') == 'ksgrs':
        type_form = ZakazFormKSGRS
    elif request.GET.get('category') == 'truba':
        type_form = ZakazFormTrub
    else:
        messages.error(request, 'Неверная категория заказа.')
        return redirect('bank:bank_list')
    if request.method == 'POST':
        form = type_form(request.POST)
        if form.is_valid():
            return make_zakaz(form)
    else:
        form = type_form()
    
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
    transport = zakazy.filter(zakazitem__material__category__pk=3).count()
    truba = zakazy.filter(zakazitem__material__category__pk=1).count()*20
    obuchenie.lin = zakazy.filter(zakazitem__material__pk=12)
    obuchenie.grs = zakazy.filter(zakazitem__material__pk=13)
    obuchenie.ks = zakazy.filter(zakazitem__material__pk=14)
    zakazy_lin = zakazy.filter(zakazitem__material__category__pk=1).count()
    zakazy_grs = zakazy.filter(zakazitem__material__pk=10).count()
    zakazy_ks = zakazy.filter(zakazitem__material__pk=11).count()
    zakazy_shtraf = zakazy.filter(zakazitem__material__category__pk=4).count()

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
    }
    return render(request, 'bank/team_detail.html', context)

@login_required
def zakaz_kapremont(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    balance = Balance.objects.get(team=team)
    items = ZakazItem.objects.filter(zakaz__status__name='Выдан снабженцем', zakaz__team=team)
    materials = Stock.objects.filter(warehouse__team=team)
    zakaz_form = ZakazFormTrub()
    return render(request, 'bank/zakaz_kapremont.html', {'team': team, 'items': items, 'materials': materials, 'balance': balance, 'form': zakaz_form})