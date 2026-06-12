from django.urls import path
from app.cashflow import views


urlpatterns = [
    path('baul/', views.BaulListCreateAPIView.as_view(), name='baul-list-create'),
    path('baul/resumen/', views.BaulResumenAPIView.as_view(), name='baul-resumen'),
    path('baul/resumen/<int:anio_id>/<int:mes_id>/', views.BaulResumenMensualAPIView.as_view(), name='baul-resumen-mensual'),
    path('baul/<int:baul_id>/', views.BaulDetailAPIView.as_view(), name='baul-detail'),

    path('ingresos/<int:anio_id>/<int:mes_id>/', views.IngresosListAPIView.as_view(), name='ingresos-list'),
    path('ingresos/create/', views.IngresosCreateAPIView.as_view(), name='ingresos-create'),
    path('ingresos/update/<int:ingreso_id>/', views.IngresosUpdateAPIView.as_view(), name='ingresos-update'),
    path('ingresos/delete/<int:ingreso_id>/', views.IngresosDeleteAPIView.as_view(), name='ingresos-delete'),
    path('ingresos/detail/<int:ingreso_id>/', views.IngresosDetailAPIView.as_view(), name='ingresos-detail'),


    # Endpoints para Egresos
    path('egresos/<int:anio_id>/<int:mes_id>/', views.EgresosListAPIView.as_view(), name='egresos-list'),
    path('egresos/create/', views.EgresosCreateAPIView.as_view(), name='egresos-create'),
    path('egresos/update/<int:egreso_id>/', views.EgresosUpdateAPIView.as_view(), name='egresos-update'),
    path('egresos/delete/<int:egreso_id>/', views.EgresosDeleteAPIView.as_view(), name='egresos-delete'),
    path('egresos/detail/<int:egreso_id>/', views.EgresosDetailAPIView.as_view(), name='egresos-detail'),


    #Finanzas
    path('finanzas/<int:anio_id>/<int:mes_id>/', views.FinanzasSummaryAPIView.as_view(), name='finanzas-summary'),

    # Reportes
   path('egresos/<int:anio_id>/<int:mes_id>/resumen-categorias/', views.EgresosResumenPorCategoriaAPIView.as_view(), name='egresos-resumen-categorias'),
]
