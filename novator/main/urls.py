from django.urls import path

from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('team/<int:pk>/', views.team, name='team'),
    #path('control/', views.control, name='control'),
    path('next_year/', views.next_year, name='next_year'),
    path('end_game/', views.end_game, name='end_game'),
    path('control/', views.control, name='control'),

]