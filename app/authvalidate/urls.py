from django.urls import path
from app.authvalidate import views


urlpatterns = [
    path('validate-email/<int:userID>/<str:token>',
         views.ValidateEmail.as_view()),
    path('update-password', views.ChangePassword.as_view()),
    path('reset-password', views.ResetPassword.as_view()),
    path('update-reset-password/<int:userID>/<str:token>',
         views.updateResetPassword.as_view()),
]
