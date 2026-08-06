from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction
from django.contrib import messages
from bank.models import Balance, Zakaz, ZakazItem
from main.models import Status, Team, ItemProperty
from bank.func import give_money, calculate_win_score, end_game
from mtr.models import Stock, Sklad, Shipment
from django.db.models import Sum
from .models import ComissonScores, Team
from bank.models import Balance, Zakaz
from bank.forms import ComissionScoreForm
from constance import config

# Create your views here.

@login_required
def index(request):
    teams = Team.objects.all()
    context = {
        'teams': teams,
        'year': config.YEAR,

    }
    return render(request, 'main/index.html', context)

@login_required
def team(request, pk):
    team = get_object_or_404(Team, pk=pk)
    balance = Balance.objects.get(team=team)
    zakaz = Zakaz.objects.filter(team=team)
    context = {
        'team': team,
        'balance': balance,
        'zakaz': zakaz,
    }
    return render(request, 'main/team.html', context)

@login_required
@transaction.atomic
def next_year(request):
    if request.method == 'POST':
        config.YEAR = request.POST.get('year', config.YEAR)
        for team in Team.objects.filter(status=True):
            give_money(team)
    return render(request, 'main/next_year.html', {'year': config.YEAR,
                                                   'bonus': config.MONEY_PER_YEAR })

@login_required
@transaction.atomic
def end_game_func(request):
    if request.method == 'POST':
        for team in Team.objects.filter(status=True):
            end_game(team)
    return render(request, 'main/end_game.html')


def build_statistics_context():
    teams = Team.objects.filter(status=True).order_by('pk')
    stock = Stock.objects.filter(warehouse__team__in=teams)
    sklad = Sklad.objects.filter(is_active=True, team=None)
    stock_by_skalad = Stock.objects.filter(warehouse__in=sklad, material__category__slug__in=['trubi', 'ks', 'eco'])
    stock_by_skalad_grs = Shipment.objects.filter(from_warehouse__in=sklad, material__category__slug='grs').count()
    zakaz_items_premii = ZakazItem.objects.filter(material__category__slug='premii')
    bally = ItemProperty.objects.filter(property_name='winner_score')

    teams_items = []
    teams_grs = []
    win_score = []
    total_potrebiteli = []
    win_score_map = {}
    team_stats = []
    for team in teams:
        total_potrebitel = 0
        team_stock = Stock.objects.filter(warehouse__team=team)
        score = calculate_win_score(team)
        win_score.append({'team': team, 'score': score})
        win_score_map[team.pk] = score
        total = team_stock.filter(material__category__slug='trubi').aggregate(total=Sum('quantity'))['total'] or 0
        total_grs = team_stock.filter(material__category__slug='grs').aggregate(total=Sum('quantity'))['total'] or 0
        for grs in ZakazItem.objects.filter(zakaz__team=team, material__category__slug='grs', zakaz__status__pk=5):
            total_potrebitel += float(ItemProperty.objects.get(material=grs.material, property_name='potrebitel').property_value)
        total_potrebiteli.append({'team': team, 'total_potrebitel': total_potrebitel})
        teams_items.append({'team': team, 'items_count': total * 20})
        teams_grs.append({'team': team, 'total_grs': total_grs})

        balance = getattr(team, 'balance', None)
        achievements = []
        for item in zakaz_items_premii:
            if item.zakaz.team_id != team.pk:
                continue
            ball_value = ''
            for ball in bally:
                if ball.material_id == item.material_id:
                    ball_value = ball.property_value
                    break
            achievements.append({'material_name': item.material.name, 'ball_value': ball_value})

        team_stats.append({
            'team': team,
            'balance': balance.money if balance is not None else 0,
            'purchased_pipe_km': total * 20,
            'grs_count': total_grs,
            'consumers': total_potrebitel,
            'achievements': achievements,
            'eco_score': getattr(getattr(team, 'eco_scores', None), 'score', 0),
            'win_score': score,
        })

    teams_sorted = sorted(teams, key=lambda team: win_score_map.get(team.pk, 0), reverse=True)

    return {
        'teams': teams,
        'teams_sorted': teams_sorted,
        'sklad': sklad,
        'stock': stock,
        'stock_by_skalad': stock_by_skalad,
        'teams_items': teams_items,
        'teams_grs': teams_grs,
        'stock_by_skalad_grs': stock_by_skalad_grs,
        'win_score': win_score,
        'zakaz_items_premii': zakaz_items_premii,
        'bally': bally,
        'total_potrebiteli': total_potrebiteli,
        'team_stats': team_stats,
        'year': config.YEAR,
    }


def make_comisson_scores(request):
    if request.method == 'POST':
        form = ComissionScoreForm(request.POST, user=request.user)
        if form.is_valid():
            team = form.cleaned_data['team']
            score1 = form.cleaned_data['score1']
            score2 = form.cleaned_data['score2']
            score3 = form.cleaned_data['score3']
            score4 = form.cleaned_data['score4']
            score5 = form.cleaned_data['score5']
            calculate_score = (score1 + score2 + score3 + score4 + score5)/5
            comisson_score = ComissonScores.objects.update_or_create(team_id=team, defaults={'score': calculate_score, 'score1': score1, 'score2': score2,'score3': score3,'score4': score4,'score5': score5,})
            messages.success(request, f"Баллы комиссии в размере {calculate_score} для команды {team} успешно внесены.")
            return redirect('main:make_comisson_scores')
    form = ComissionScoreForm(user=request.user)
    return render(request, 'main/comission.html', {'form': form, 'scores': ComissonScores.objects.all().order_by('pk')})


@login_required
def control(request):
    return render(request, 'main/control.html', build_statistics_context())


@login_required
def statistics_page(request):
    return render(request, 'main/statistics.html', build_statistics_context())


@login_required
def presentation_statistics_page(request):
    return render(request, 'main/presentation_statistics.html', build_statistics_context())

@login_required
def presentation_statistics_end_game_page(request):
    return render(request, 'main/presentation_statistics_end_game.html', build_statistics_context())