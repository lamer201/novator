from django.urls import path
from . import views

app_name = 'contactor'

urlpatterns = [
    path('', views.index, name='index'),
]