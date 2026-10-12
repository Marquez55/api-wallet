from django.urls import path

from app.agenda import views


urlpatterns = [
    path('events/', views.AgendaEventoListCreateAPIView.as_view(), name='agenda-event-list-create'),
    path('events/<int:pk>/', views.AgendaEventoDetailAPIView.as_view(), name='agenda-event-detail'),
]
