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
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from users.views import UserViewSet
from groups.views import GroupViewSet
from contributions.views import ContributionViewSet
from loans.views import LoanViewSet

schema_view = get_schema_view(
    openapi.Info(
        title="eChama API",
        default_version='v1',
        description="API documentation for the eChama project",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="isaack.jyevisa@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


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
    path('api/loans/', include('loans.urls')),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]
