"""
URL configuration for echama_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet
from groups.views import GroupViewSet
from contributions.views import ContributionViewSet
from loans.views import LoanViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'contributions', ContributionViewSet)
router.register(r'loans', LoanViewSet)

@api_view(['GET'])
def test_api(request):
    return Response({"message": "It works!"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/ping/', test_api),
    path('api/users/', include('users.urls')),
    path('api/groups/', include('groups.urls')), 
    path('api/contributions/', include('contributions.urls')),
    path('api/loans/', include('loans.urls'))
]
