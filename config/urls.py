from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="API Wallet",
        default_version='v1',
        description="Documentación API Wallet Nexuz",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="hgsmarquez@outlook.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('admin/', admin.site.urls),

    # Rutas para JWT usando Simple JWT
    path('auth/api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),


    path('auth/', include('app.authentication.urls')),
    path('user/', include('app.user.urls')),
    path('company/', include('app.company.urls')),

    path('catalogos/', include('app.catalogos.urls')),

    path('control/', include('app.cashflow.urls')),

    path('dashboard/', include('app.resume.urls'))


]
