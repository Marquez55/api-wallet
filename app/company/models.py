from django.db import models



class Company(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.CharField(max_length=500, blank=True)
    direccion = models.CharField(max_length=200, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return "{}".format(self.nombre)

    class Meta:
        app_label = 'company'