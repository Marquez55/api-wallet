"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path, include

from rest_framework import permissions
from rest_framework_jwt.views import refresh_jwt_token, verify_jwt_token, obtain_jwt_token
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Carrera Issstep API",
        default_version='v1',
        description="Documentación de la API",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="hgsmarquez@outlook.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('', schema_view.with_ui(
         'swagger', cache_timeout=0), name='schema-swagger-ui'),

    path('auth/api-auth/', obtain_jwt_token, name='news-year-archive'),
    path('auth/api-auth-refresh/', refresh_jwt_token),
    path('auth/api-token-verify/', verify_jwt_token),
    path('admin/', admin.site.urls),
    path('user/', include('app.user.urls')),
    path('auth/', include('app.authvalidate.urls')),
    path('empresa', include('app.empresa.urls')),
    path('participantes', include('app.participantes.urls')),
    
]
