from django.db import models
from django.contrib.auth.models import User
# Create your models here.

from app.empresa.models import Empresa


class Rol(models.Model):
    clave = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=50)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return "{} - {}".format(self.clv, self.descripcion)

    class Meta:
        app_label = 'user'


class Perfil(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.PROTECT, primary_key=True, related_name='perfil_user_set')
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT,
                            related_name='perfil_rol_set')
    empresa = models.ForeignKey(
        Empresa, null=True, on_delete=models.PROTECT, related_name='perfil_empresa_set')

    def __str__(self):
        return "{}".format(self.user.id)

    class Meta:
        app_label = 'user'
