from django.urls import path, include

urlpatterns = [
    path('auth/', include('user_auth.api.urls')),
    path('job/', include('job.api.urls')),
]
