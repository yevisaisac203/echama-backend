from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GroupViewSet

router = DefaultRouter()
router.register(r'', GroupViewSet)  # Register the GroupViewSet

urlpatterns = [
    path('', include(router.urls)),  # Include the router's URLs
]