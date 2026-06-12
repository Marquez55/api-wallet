from django.db import models
from django.contrib.auth.models import User
from app.catalogos.models import AnioUsuario, Mes, Tipo, TipoIngreso, Categoria, Subcategoria


class BaulDisponible(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=300)
    tipo = models.CharField(max_length=100, blank=True, default='')
    descripcion = models.TextField(blank=True, null=True)
    saldo_inicial = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - {self.usuario.username}"


class Ingresos(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    anio = models.ForeignKey(AnioUsuario, on_delete=models.CASCADE)
    mes = models.ForeignKey(Mes, on_delete=models.CASCADE)
    fecha = models.DateField()
    tipo = models.ForeignKey(Tipo, on_delete=models.CASCADE)
    tipoingreso = models.ForeignKey(TipoIngreso, on_delete=models.CASCADE)
    baul = models.ForeignKey(BaulDisponible, on_delete=models.SET_NULL, null=True, blank=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.fecha} - {self.tipo} - {self.monto}"


class Egresos(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    anio = models.ForeignKey(AnioUsuario, on_delete=models.CASCADE)
    mes = models.ForeignKey(Mes, on_delete=models.CASCADE)
    fecha = models.DateField()
    tipo = models.ForeignKey(Tipo, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    subcategoria = models.ForeignKey(Subcategoria, on_delete=models.CASCADE, null=True, blank=True)
    baul = models.ForeignKey(BaulDisponible, on_delete=models.SET_NULL, null=True, blank=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.fecha} - {self.categoria} - {self.subcategoria} - {self.monto}"
