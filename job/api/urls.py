from django.urls import path
from .views import SearchKeyWordView,FetchSingleJobView,FetchSaveJobListView


urlpatterns = [
    path('searchKeyword/', SearchKeyWordView.as_view(), name='searchKeyword'),
    path('fetchSingleJob/', FetchSingleJobView.as_view(), name='fetchSingleJob'),
    path('fetchSavedJobList/',FetchSaveJobListView.as_view(), name='fetchSavedJobList')
]