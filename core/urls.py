from django.contrib import admin
from django.urls import path, include
from django.urls import get_resolver
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.api.urls')),
]
