from django.urls import path
from .views import LoginView
from .views import GoogleCallbackView


urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('google/callback/', GoogleCallbackView.as_view(), name='google_callback')
]