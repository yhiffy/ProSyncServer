from django.urls import path

from .views import LoginView,RegisterView,ActivateView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/', ActivateView.as_view(), name='activate'),
]