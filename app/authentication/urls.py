from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from app.authentication import views

urlpatterns = [
    path('validate-email/<str:token>', views.ValidateEmail.as_view(), name='validate-email'),
    path('update-password', views.ChangePassword.as_view()),
    path('reset-password', views.ResetPassword.as_view()),
    path('update-reset-password/<str:token>', views.updateResetPassword.as_view()),

    # Rutas JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
