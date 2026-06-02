from django.urls import path
from . import views

app_name = 'audit'

urlpatterns = [
    path('', views.index, name='index'),
    path('team/<int:team_id>/', views.team_detail, name='team_detail'),
    path('team/<int:team_id>/audit/', views.team_audit, name='team_audit'),
    path('shtraf/', views.shtraf, name='shtraf'),
]