from django.db import models
from django.contrib.auth.models import User
from app.company.models import Company


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
    company = models.ForeignKey(
        Company, null=True, on_delete=models.PROTECT, related_name='perfil_company_set')

    def __str__(self):
        return "{}".format(self.user.id)

    class Meta:
        app_label = 'user'


class Usuario(models.Model):
    nombre = models.CharField(max_length=150, blank=False, null=False)
    apellidoP = models.CharField(max_length=150, blank=False, null=False)
    apellidoM = models.CharField(max_length=150, blank=False, null=False)
    email = models.EmailField(blank=False, null=False)
    activo = models.BooleanField(default=False)
    empresa = models.ForeignKey(
        Company, null=True, on_delete=models.PROTECT, related_name='fisico_empresa_set')
    rol = models.ForeignKey(
        Rol, null=True, on_delete=models.PROTECT, related_name='fisico_rol_set')


    def __str__(self):
        return f"Usuario: {self.nombre}"


class Administradores(models.Model):
    nombre = models.CharField(max_length=150, blank=False, null=False)
    apellidoP = models.CharField(max_length=150, blank=False, null=False)
    apellidoM = models.CharField(max_length=150, blank=False, null=False)
    email = models.EmailField(blank=False, null=False)
    activo = models.BooleanField(default=False)
    empresa = models.ForeignKey(
        Company, null=True, on_delete=models.PROTECT, related_name='admin_empresa_set')
    rol = models.ForeignKey(
        Rol, null=True, on_delete=models.PROTECT, related_name='admin_rol_set')

    def __str__(self):
        return f"administrador: {self.nombre}"