from django.contrib import messages
from django.shortcuts import redirect, render
from bank.models import Zakaz, ZakazItem
from main.models import Status, Team
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.views.decorators.http import require_POST

# Create your views here.
def index(request):
    zakazy = Zakaz.objects.filter(category__slug='learning', status__pk=2, payment=True)
    zakazy_items = ZakazItem.objects.filter(zakaz__in=zakazy)
    return render(request, 'learning/index.html', {'zakazy': zakazy, 'zakazy_items': zakazy_items})


@login_required
@require_POST
@transaction.atomic
def success_learning(request, zakaz_id):
    zakaz = Zakaz.objects.get(id=zakaz_id)
    zakaz.status = Status.objects.get(name='Завершен')
    team = Team.objects.get(id=zakaz.team.id)
    zakaz.save()
    zakaz_items = ZakazItem.objects.filter(zakaz=zakaz)
    for item in zakaz_items:
        if item.material.slug == 'learn_ks':
            team.learn_ks = True
        if item.material.slug == 'learn_grs':
            team.learn_grs = True
        if item.material.slug == 'learn_les':
            team.learn_les = True
    team.save()
    messages.success(request, 'Обучение успешно завершено!')
    return redirect('learning:index')