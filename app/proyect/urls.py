from django.urls import path
from app.proyect import views


urlpatterns = [
    path('', views.ProyectListView.as_view(), name='proyect'),
    path('<int:pk>/', views.ProyectDetailView.as_view(), name='proyect-detail'),
    path('<int:proyecto_id>/pagos/', views.PagoProyectoListCreateView.as_view(), name='pago-proyect-list'),
    path('pagos/<int:pk>/', views.PagoProyectoDetailView.as_view(), name='pago-proyect-detail'),
]
