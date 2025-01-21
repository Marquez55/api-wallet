from django.db import models
from django.contrib.auth.models import User
from app.catalogos.models import AnioUsuario, Mes, Tipo, TipoIngreso, Categoria, Subcategoria



class Ingresos(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    anio = models.ForeignKey(AnioUsuario, on_delete=models.CASCADE)
    mes = models.ForeignKey(Mes, on_delete=models.CASCADE)
    fecha = models.DateField()  # Campo para la fecha del ingreso
    tipo = models.ForeignKey(Tipo, on_delete=models.CASCADE)  # Relación al tipo (Ingreso/Egreso)
    tipoingreso = models.ForeignKey(TipoIngreso, on_delete=models.CASCADE)  # Relación al tipo de ingreso (Salario, etc.)
    monto = models.DecimalField(max_digits=10, decimal_places=2)  # Monto con hasta 2 decimales
    descripcion = models.TextField(blank=True, null=True)  # Descripción opcional
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.fecha} - {self.tipo} - {self.monto}"


class Egresos(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    anio = models.ForeignKey(AnioUsuario, on_delete=models.CASCADE)
    mes = models.ForeignKey(Mes, on_delete=models.CASCADE)
    fecha = models.DateField()  # Fecha del egreso
    tipo = models.ForeignKey(Tipo, on_delete=models.CASCADE)  # Relación al tipo (Ingreso/Egreso)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)  # Relación con categoría
    subcategoria = models.ForeignKey(Subcategoria, on_delete=models.CASCADE, null=True, blank=True)  # Permitir null
    monto = models.DecimalField(max_digits=10, decimal_places=2)  # Monto del egreso
    descripcion = models.TextField(blank=True, null=True)  # Descripción opcional
    activo = models.BooleanField(default=True)  # Indicador de activación

    def __str__(self):
        return f"{self.usuario.username} - {self.fecha} - {self.categoria} - {self.subcategoria} - {self.monto}"