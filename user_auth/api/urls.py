from django.urls import path
from .views import LoginView,RegisterView,ActivateView,UserInfoView,GoogleLoginView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/', ActivateView.as_view(), name='activate'),
    path('userInfo/', UserInfoView.as_view(), name='userInfo'),
    path('google/', GoogleLoginView.as_view(), name='google'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]