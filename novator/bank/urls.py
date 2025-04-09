from django.urls import path

from . import views

app_name = 'bank'

urlpatterns = [
    path('zakaz/', views.create_zakaz, name='create_zakaz'),
]