from django.urls import path
from app.catalogos import views


urlpatterns = [

    path('anios/', views.CatalogoAniosAPIView.as_view(), name='list_anios'),
    path('anios/crear/', views.CrearAnioAPIView.as_view(), name='crear_anio'),
    path('anios/<int:anio_id>/', views.AnioDetailAPIView.as_view(), name='detalle_anio'),
    path('anios/<int:anio_id>/actualizar/', views.ActualizarAnioAPIView.as_view(), name='actualizar_anio'),
    path('anios/<int:anio_id>/activar/', views.ActivarAnioAPIView.as_view(), name='activar_anio'),
    path('mes', views.MesesAPIView.as_view(), name='list_mes'),

    path('tipos', views.TipoListView.as_view(), name='tipo-list'),

    path('tingresos', views.TipoIngresoAPIView.as_view(), name='tipo-ingreso'),

    #Servicios de Categorias
    path('categorias/', views.CategoriaListCreateAPIView.as_view(), name='categoria-list-create'),

    path('categorias/<int:pk>/', views.CategoriaUpdateDeleteAPIView.as_view(), name='categoria-update-delete'),

    #Servicios de Subcategorias
    path('categorias/<int:categoria_id>/subcategorias/', views.SubcategoriaListCreateAPIView.as_view(), name='subcategoria-list-create'),
    path('subcategorias/<int:pk>/', views.SubcategoriaUpdateDeleteAPIView.as_view(), name='subcategoria-update-delete'),
]
