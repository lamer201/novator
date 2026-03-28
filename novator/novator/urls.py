from django.contrib import admin
from django.urls import include, path
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('bank/', include('bank.urls', namespace = 'bank')),
    path('mtr/', include('mtr.urls', namespace = 'mtr')),
    path('', include('main.urls', namespace = 'main')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns