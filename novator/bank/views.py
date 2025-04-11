from django.shortcuts import get_list_or_404, render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .froms import ZakazForm
from .models import Balance, Buy

@login_required
def create_zakaz(request):
    if request.method == 'POST':
        form = ZakazForm(request.POST or None)
        if form.is_valid():
            zakaz = form.save(commit=False)
            zakaz.save()
            buy = Buy()
            buy.team = zakaz.team
            buy.year = 1
            for i in zakaz.material.all():
                buy.material = i.material
                buy.save()
        return redirect(f'/team/{zakaz.team.pk}/', 'main/index.html')
    form = ZakazForm()
    return render(request, 'bank/zakaz.html', {'form': form})