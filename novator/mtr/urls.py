from django.urls import path
from . import views

app_name = 'mtr'

urlpatterns = [
    path('', views.index, name='index'),
    path('extradition/', views.extraditions, name='extraditions'),
    path('extradition_detail/<int:pk>/', views.extradition_detail, name='extradition_detail'),
    path('sklad/', views.sklad, name='sklad'),
    path('shipment/<int:pk>/', views.shipment, name='shipment'),
    #path('sklad_teams/<int:pk>/', views.sklad_teams, name='sklad_teams'),
]