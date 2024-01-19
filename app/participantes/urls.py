from django.urls import path

from app.participantes import views


urlpatterns = [
    path('', views.ParticipantesCreateAPIView.as_view()),
    path('/detalle', views.ParticipantesListAPIView.as_view(), name='listar_participantes'),
    path('/search', views.ParticipanteSearchByEmailAPIView.as_view(), name='buscar_participantes'),
]