from django.urls import path

from app.empresa import views


urlpatterns = [
    path('update', views.EmpresaUpdateView.as_view(), name='empresa-update'),
    path('get-app-url/', views.GetAppURLView.as_view(), name='get-app-url'),
]
