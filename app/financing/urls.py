from django.urls import path
from app.financing import views



urlpatterns = [
    path('prestamos/', views.PrestamoListCreateAPIView.as_view(), name='prestamo-list-create'),
    path('prestamos/<int:pk>/', views.PrestamoUpdateDeleteAPIView.as_view(), name='prestamo-update-delete'),

    path('pagos-prestamo/<int:prestamo_id>/', views.PagosPrestamoListCreateAPIView.as_view(), name='pagos-prestamo-list-create'),
    path('pagos/<int:pk>/', views.PagosUpdateDeleteAPIView.as_view(), name='pagos-update-delete'),
]