from django.urls import path

from . import views

app_name = 'bank'

urlpatterns = [
    path('', views.bank_list, name='bank_list'),
    path('create_zakaz', views.create_zakaz, name='create_zakaz'),
    path('<int:zakaz_id>/', views.zakaz_detail, name='zakaz_detail'),
    path('zakaz_list/', views.zakaz_list, name='zakaz_list'),
    path('team/<int:team_id>/', views.team_detail, name='team_detail'),
    path('<int:zakaz_id>/edit', views.zakaz_edit, name='zakaz_edit'),
    path('get-balance/<int:team_id>/', views.check_balance, name='get_balance'),
    path('zakaz/<int:zakaz_id>/otmena/', views.zakaz_otmena, name='zakaz_otmena'),
    path('zakaz/<int:zakaz_id>/delete/', views.zakaz_delete, name='zakaz_delete'),
    #path('zakaz_add_material/<int:zakaz_id>/', views.zakaz_add_material, name='zakaz_add_material'),
    path('zakaz/<int:zakaz_id>/issued/', views.zakaz_issued, name='zakaz_issued'),
]