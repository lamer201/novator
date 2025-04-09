from django.shortcuts import render, redirect
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

        return redirect(f'/team/{zakaz.team.pk}/', 'main/index.html')
    form = ZakazForm()
    return render(request, 'bank/zakaz.html', {'form': form})