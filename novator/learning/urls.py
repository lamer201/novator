from django.urls import path
from . import views

app_name = 'learning'

urlpatterns = [
    path('', views.index, name='index'),
    #path('zakaz_detail/<int:pk>/', views.zakaz_detail, name='zakaz_detail'),
    path('success_learning/<int:zakaz_id>/', views.success_learning, name='success_learning'),
    path('team_detail/<int:team_id>/', views.team_detail, name='team_detail'),
    path('create_premii/<int:team_id>/', views.create_premii, name='create_premii'),
]