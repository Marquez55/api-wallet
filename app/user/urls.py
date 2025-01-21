from django.urls import path
from app.user import views


urlpatterns = [
    path('info', views.UsuarioInfoAPIView.as_view(), name='usuario-info'),
]
