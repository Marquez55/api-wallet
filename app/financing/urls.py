from django.urls import path
from app.financing import views



urlpatterns = [
    path('prestamos/', views.PrestamoListCreateAPIView.as_view(), name='prestamo-list-create'),
    path('prestamos/<int:pk>/', views.PrestamoUpdateDeleteAPIView.as_view(), name='prestamo-update-delete'),
    path('prestamos/<int:prestamo_id>/', views.PrestamoRetrieveAPIView.as_view(), name='prestamo-detail'),




    path('pagos-prestamo/<int:prestamo_id>/', views.PagosPrestamoListCreateAPIView.as_view(), name='pagos-prestamo-list-create'),
    path('pagos/<int:pk>/', views.PagosUpdateDeleteAPIView.as_view(), name='pagos-update-delete'),

    path('prestamos/total/', views.ResumenGeneralPrestamosAPIView.as_view(), name='total-prestamos'),



    path('conceptos/', views.ConceptoPrestamoAPIView.as_view(), name='concepto-prestamo-list-create'),
    path('conceptos-prestamo/<int:pk>/', views.ConceptoPrestamoAPIView.as_view(), name='concepto-prestamo-update-delete'),
]