from django.urls import path
from .views import SearchKeyWordView,FetchSingleJobView


urlpatterns = [
    path('searchKeyword/', SearchKeyWordView.as_view(), name='searchKeyword'),
    path('fetchSingleJob/', FetchSingleJobView.as_view(), name='fetchSingleJob')

]