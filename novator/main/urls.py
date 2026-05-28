from django.urls import path

from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('team/<int:pk>/', views.team, name='team'),
    #path('control/', views.control, name='control'),
    path('control/', views.next_year, name='next_year'),
]