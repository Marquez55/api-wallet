from django.urls import path

from app.empresa import views


urlpatterns = [
    path('', views.EmpresaAPIView.as_view()),
]
