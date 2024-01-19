from django.db import models

class Participante(models.Model):
    nombre = models.CharField(max_length=150)
    apellidos = models.CharField(max_length=150)
    email = models.EmailField()
    sexo = models.CharField(max_length=20)
    numero_de_participante = models.PositiveIntegerField(unique=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return "{} {}".format(self.nombre, self.apellidos)

    class Meta:
        app_label = 'participantes'