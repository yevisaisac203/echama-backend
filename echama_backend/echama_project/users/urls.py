from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

router = DefaultRouter()
router.register(r'', UserViewSet)  # Register the UserViewSet

urlpatterns = [
    path('', include(router.urls)),  # Include the router's URLs
]