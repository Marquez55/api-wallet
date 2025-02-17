from django.urls import path
from app.user import views


urlpatterns = [
    path('info', views.UsuarioInfoAPIView.as_view(), name='usuario-info'),
    path('usuarios/', views.ListUserAPIView.as_view(), name='list-users'),
    path('new/usuarios/', views.CreateUserAPIView.as_view(), name='create-users'),

    path('update/<int:user_id>/', views.UpdateUserAPIView.as_view(), name='update-user'),

    path('<int:user_id>/update-avatar/', views.UpdateAvatarAPIView.as_view(), name='update-avatar'),

    path('<int:user_id>/update-theme/', views.UpdateThemeAPIView.as_view(), name='update-theme'),
]
