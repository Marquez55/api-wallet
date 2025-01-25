from django.urls import path
from app.resume import views



urlpatterns = [
    path('egresos/favoritos/', views.EgresosFavoritosAPIView.as_view(), name= 'egresos-favoritos'),
    path('totales', views.IngresosEgresosAPIView.as_view(), name= 'totales-cashflow'),
    path('meses', views.IngresosEgresosMensualesAPIView.as_view(), name= 'mensuales-cashflow'),
    path('salario/meses/', views.IngresosMensualesSalarioAPIView.as_view(), name= 'ingresos-mensuales')
]