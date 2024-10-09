from django.urls import path
from .views import SearchKeyWordView


urlpatterns = [
    path('searchKeyword/', SearchKeyWordView.as_view(), name='searchKeyword'),

]