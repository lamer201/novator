from django.shortcuts import get_list_or_404, get_object_or_404, render, redirect
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .models import Balance, Buy, Team, Zakaz, Material, ZakazItem, Status

def get_sum(form):
    sum_material=0
    koeff = float(form.cleaned_data['koeff'])
    for field, quantity in form.cleaned_data.items():
        if field != 'team' and field != 'koeff' and quantity:
                    material = get_list_or_404(Material, slug=field)[0]
                    price = material.price*koeff
                    sum_material = sum_material + (price*quantity)
    return sum_material

def check_balance(request, team_id):
    try:
        item = Balance.objects.get(team=team_id)
        # Возвращаем нужное поле в JSON
        return JsonResponse({'text': item.money})
    except Balance.DoesNotExist:
        return JsonResponse({'text': ''}, status=404)


def make_zakaz(form):
    # Get form data
    team = Team.objects.get(pk=form.cleaned_data['team']) 
    balance = Balance.objects.get(team=team)     
    test_balance = get_sum(form)
    if test_balance > balance.money:
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
        if field != 'team' and field != 'koeff' and quantity:
            material = get_list_or_404(Material, slug=field)[0]
            koeff = float(form.cleaned_data['koeff'])
            price = material.price * koeff
            zakazItem = ZakazItem.objects.create(
                zakaz=zakaz,
                material=material,
                price=price,
                quantity=quantity,
                koeff=koeff
            )
            zakazItem.save()
        
    new_balance = balance.money - test_balance
    balance.money = new_balance
    balance.save()
    return redirect('bank:zakaz_detail', zakaz_id=zakaz.pk)  # Replace with your success URL

