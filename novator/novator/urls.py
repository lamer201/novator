from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('bank.urls', namespace = 'bank')),
    path('', include('main.urls', namespace = 'main')),
]
