from django.urls import path
from . import views

app_name = 'contactor'

urlpatterns = [
    path('', views.index, name='index'),
    path('team/<int:team_id>/', views.team_detail, name='team_detail'),
    path('create_eco_compensation/<int:zakaz_id>/', views.create_eco_compensation, name='create_eco_compensation'),
]