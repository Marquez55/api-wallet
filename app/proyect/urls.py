from django.urls import path
from app.proyect import views


urlpatterns = [
    path('budgets/', views.PresupuestoListView.as_view(), name='budget-list'),
    path('budgets/<int:pk>/', views.PresupuestoDetailView.as_view(), name='budget-detail'),
    path('budgets/<int:presupuesto_id>/categories/', views.PresupuestoCategoriaListCreateView.as_view(), name='budget-category-list'),
    path('budgets/categories/<int:pk>/', views.PresupuestoCategoriaDetailView.as_view(), name='budget-category-detail'),
    path('budgets/<int:presupuesto_id>/items/', views.PresupuestoPartidaListCreateView.as_view(), name='budget-item-list'),
    path('budgets/items/<int:pk>/', views.PresupuestoPartidaDetailView.as_view(), name='budget-item-detail'),
    path('', views.ProyectListView.as_view(), name='proyect'),
    path('<int:pk>/', views.ProyectDetailView.as_view(), name='proyect-detail'),
    path('<int:proyecto_id>/pagos/', views.PagoProyectoListCreateView.as_view(), name='pago-proyect-list'),
    path('pagos/<int:pk>/', views.PagoProyectoDetailView.as_view(), name='pago-proyect-detail'),
]
