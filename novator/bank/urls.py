from django.urls import path

from . import views

app_name = 'bank'

urlpatterns = [
    path('', views.bank_list, name='bank_list'),
    path('create_zakaz', views.create_zakaz, name='create_zakaz'),
    path('<int:zakaz_id>/', views.zakaz_detail, name='zakaz_detail'),
    path('zakaz_list/', views.zakaz_list, name='zakaz_list'),
]