from rest_framework.routers import DefaultRouter
from django.urls import path, include
from auth.api.urls import auth_router

router = DefaultRouter()

#auth Routers
router.registry.extend(auth_router.registry)

urlpatterns = [
    path('', include(router.urls)),
]
