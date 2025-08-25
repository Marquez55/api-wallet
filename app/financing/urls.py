from django.urls import path
from app.financing import views



urlpatterns = [
    # Prestamos
    path('prestamos/', views.PrestamoListCreateAPIView.as_view(), name='prestamo-list-create'),
    path('prestamos/<int:prestamo_id>/detalle/', views.PrestamoRetrieveAPIView.as_view(), name='prestamo-detail'),
    path('prestamos/<int:pk>/', views.PrestamoUpdateDeleteAPIView.as_view(), name='prestamo-update-delete'),

    # Pagos de prestamo
    path('pagos-prestamo/<int:prestamo_id>/', views.PagosPrestamoListCreateAPIView.as_view(), name='pagos-prestamo-list-create'),
    path('pagos/<int:pk>/', views.PagosUpdateDeleteAPIView.as_view(), name='pagos-update-delete'),

    # Resumen prestamos
    path('prestamos/total/', views.ResumenGeneralPrestamosAPIView.as_view(), name='total-prestamos'),

    # Conceptos prestamo
    path('conceptos/', views.ConceptoPrestamoAPIView.as_view(), name='concepto-prestamo-list-create'),
    path('conceptos-prestamo/<int:pk>/', views.ConceptoPrestamoAPIView.as_view(), name='concepto-prestamo-update-delete'),

    # Tarjetas de crédito
    path('tarjetas-credito/', views.CardCreditoListCreateAPIView.as_view(), name='tarjeta-credito-list-create'),
    path('tarjetas-credito/<int:tarjeta_id>/detalle/', views.CardCreditoRetrieveAPIView.as_view(), name='tarjeta-credito-detail'),
    path('tarjetas-credito/<int:tarjeta_id>/resumen/', views.ResumenTarjetaCreditoAPIView.as_view(), name='tarjeta-credito-resumen'),
    path('tarjetas-credito/<int:pk>/', views.CardCreditoUpdateDeleteAPIView.as_view(), name='tarjeta-credito-update-delete'),

    # Compras de tarjeta
    path('compras-tarjeta/<int:tarjeta_id>/', views.ComprasTarjetaCreditoListCreateAPIView.as_view(), name='compras-tarjeta-list-create'),
    path('actualizacion-compra/<int:pk>/', views.ComprasTarjetaCreditoUpdateDeleteAPIView.as_view(), name='compras-tarjeta-update-delete'),

    # Pagos de tarjeta
    path('tarjetas-credito/<int:tarjeta_id>/pagos/', views.PagoTarjetaCreditoListCreateAPIView.as_view(),
         name='pagos-list-create'),
    path('pagos-credito/<int:pk>/', views.PagoTarjetaCreditoUpdateDeleteAPIView.as_view(),
         name='pagos-update-delete'),
]