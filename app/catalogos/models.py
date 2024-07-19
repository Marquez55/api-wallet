from django.db import models


class Anios(models.Model):
    anio = models.IntegerField(unique=True)
    activo = models.BooleanField(default=Activo)

    def __str__(self):
        return self.anio

class Mes(models.Model):
    mes = models.CharField(max_length=300)
    activo = models.BooleanField(default=Activo)

    def __str__(self):
        return self.mes

class Categorias(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo = models.ForeignKey(Tipo, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=300)
    favorito = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Tipo(models.Model):

    tipo = models.CharField(max_length=300)
    activo = models.BooleanField(default=True)


    def __str__(self):
        return self.tipo