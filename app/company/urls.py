from django.urls import path
from app.company import views


urlpatterns = [
    path('update', views.CompanyUpdateView.as_view(), name='company-update'),


]