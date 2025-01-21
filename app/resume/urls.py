from django.urls import path
from app.resume import views



urlpatterns = [
    path('egresos/favoritos/', views.EgresosFavoritosAPIView.as_view(), name= 'egresos-favoritos')
]