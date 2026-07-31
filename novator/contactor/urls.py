from django.urls import path
from . import views

app_name = 'contactor'

urlpatterns = [
    path('', views.index, name='index'),
    path('check-new-orders/', views.check_new_contactor_orders, name='check_new_contactor_orders'),
    path('team/<int:team_id>/', views.team_detail, name='team_detail'),
    path('create_eco_compensation/<int:zakaz_id>/', views.create_eco_compensation, name='create_eco_compensation'),
    path('shipment/<int:pk>/', views.shipment, name='shipment'),
    path('zakaz_spg/', views.create_zakaz_spg, name='create_zakaz_spg'),
]