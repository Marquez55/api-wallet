from django.db import models
from django.contrib.auth.models import User

class AnioUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='anios')
    anio = models.IntegerField()
    activo = models.BooleanField(default=False)

    class Meta:
        unique_together = ('usuario', 'anio')  # Evita duplicados por usuario.
        verbose_name = "Año del Usuario"
        verbose_name_plural = "Años de Usuarios"

    def __str__(self):
        return f"Año {self.anio} - Usuario: {self.usuario.username}"

    def activar(self):
        """
        Activa este año y desactiva otros años del mismo usuario.
        """
        AnioUsuario.objects.filter(usuario=self.usuario, activo=True).update(activo=False)
        self.activo = True
        self.save()

class Mes(models.Model):
    mes = models.CharField(max_length=300)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.mes


#Se crean en base al usuario una es la categoria y la otra es la subcategoria
class Categoria(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=300)
    favorito = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    def eliminar_logicamente(self):
        self.activo = False
        self.save()

#Subcategorias para categorias principales
class Subcategoria(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='subcategorias')
    nombre = models.CharField(max_length=300)
    favorito = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    def eliminar_logicamente(self):
        self.activo = False
        self.save()



#Identificar si es pasivo o activo
class Tipo(models.Model):

    tipo = models.CharField(max_length=300)
    activo = models.BooleanField(default=True)


    def __str__(self):
        return self.tipo



class TipoIngreso(models.Model):

    ingreso = models.CharField(max_length=300)
    activo = models.BooleanField(default=True)


    def __str__(self):
        return self.ingreso