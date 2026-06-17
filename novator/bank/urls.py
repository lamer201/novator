from django.urls import path

from . import views

app_name = 'bank'

urlpatterns = [
    path('', views.bank_list, name='bank_list'),
    path('create_zakaz', views.create_zakaz, name='create_zakaz'),
    path('create_zakaz_buildings', views.create_zakaz_buildings, name='create_zakaz_buildings'),
    path('create_zakaz_obuchenie', views.create_zakaz_obuchenie, name='create_zakaz_obuchenie'),
    path('<int:zakaz_id>/', views.zakaz_detail, name='zakaz_detail'),
    path('zakaz_list/', views.zakaz_list, name='zakaz_list'),
    path('team/<int:team_id>/', views.team_detail, name='team_detail'),
    path('team/<int:team_id>/create_zakaz', views.create_zakaz_team, name='create_zakaz_team'),
    path('team/<int:team_id>/create_zakaz_buildings', views.create_zakaz_buildings_team, name='create_zakaz_buildings_team'),
    path('<int:zakaz_id>/edit', views.zakaz_edit, name='zakaz_edit'),
    path('get-balance/<int:team_id>/', views.check_balance, name='get_balance'),
    path('zakaz/<int:zakaz_id>/oplata/', views.zakaz_oplata, name='zakaz_oplata'),
    path('zakaz/<int:zakaz_id>/check/', views.zakaz_check, name='zakaz_check'),
    path('zakaz/<int:zakaz_id>/otmena/', views.zakaz_otmena, name='zakaz_otmena'),
    path('zakaz/<int:zakaz_id>/delete/', views.zakaz_delete, name='zakaz_delete'),
    #path('zakaz_add_material/<int:zakaz_id>/', views.zakaz_add_material, name='zakaz_add_material'),
    path('zakaz/<int:zakaz_id>/issued/', views.zakaz_issued, name='zakaz_issued'),
    #path('zakaz/<int:zakaz_id>/payment/', views.zakaz_payment, name='zakaz_payment'),
    #path('zakaz/<int:zakaz_id>/refund/', views.zakaz_refund, name='zakaz_refund'),
    path('zakaz/<int:team_id>/kapremont/', views.zakaz_kapremont, name='zakaz_kapremont'),
    path('credits/', views.credit_list, name='credit_list'),
    path('credit/<int:credit_id>/', views.credit_detail, name='credit_detail'),
    path('credit/<int:credit_id>/payment/', views.make_payment, name='make_payment'),
    path('credit/new_credit/', views.zakaz_credit, name='new_credit'),
    path('premia/new_premia/', views.new_premia, name='new_premia'),
    path('zapusk_edit/', views.zapusk_edit, name='zapusk_edit'),
    path('check-obuchenie/<int:team_id>/', views.check_obuchenie, name='check_obuchenie')
]