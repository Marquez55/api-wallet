from django.db import models
from django.contrib.auth.models import User
from datetime import date
from app.catalogos.models import ProyectoEsquema, EstatusProyecto, MetodoPago, TipoServicio, TipoPago



class Proyecto(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    proyecto = models.CharField(max_length=300)
    cliente = models.CharField(max_length=300)
    tipo = models.ForeignKey(TipoServicio, on_delete=models.CASCADE)
    esquema = models.ForeignKey(ProyectoEsquema, on_delete=models.CASCADE)
    cotizacion = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    enganche = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    meses = models.IntegerField(default=0)
    montomensual = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estatus = models.ForeignKey(EstatusProyecto, on_delete=models.CASCADE)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.proyecto} — ${self.cotizacion:,.2f}"

    def eliminar_logicamente(self):
        self.activo = False
        self.save()


class Presupuesto(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=300)
    tipo_base = models.CharField(max_length=150, blank=True, default='')
    descripcion = models.TextField(blank=True, default='')
    monto_objetivo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    def eliminar_logicamente(self):
        self.activo = False
        self.save()


class PresupuestoCategoria(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    presupuesto = models.ForeignKey(Presupuesto, on_delete=models.CASCADE, related_name='categorias')
    padre = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='hijas'
    )
    nombre = models.CharField(max_length=300)
    descripcion = models.TextField(blank=True, default='')
    orden = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.presupuesto.nombre} / {self.nombre}"

    def eliminar_logicamente(self):
        self.activo = False
        self.save()


class PresupuestoPartida(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    presupuesto = models.ForeignKey(Presupuesto, on_delete=models.CASCADE, related_name='partidas')
    categoria = models.ForeignKey(PresupuestoCategoria, on_delete=models.CASCADE, related_name='partidas')
    concepto = models.CharField(max_length=300)
    descripcion = models.TextField(blank=True, default='')
    cantidad = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monto_estimado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    prioridad = models.CharField(max_length=50, blank=True, default='')
    comprado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.presupuesto.nombre} / {self.concepto}"

    def eliminar_logicamente(self):
        self.activo = False
        self.save()


class PagoProyecto(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    tipo_pago = models.ForeignKey(TipoPago, on_delete=models.CASCADE)
    metodo = models.ForeignKey(MetodoPago, on_delete=models.CASCADE)
    fecha = models.DateField(default=date.today)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.proyecto} ${self.monto:,.2f}"

    def eliminar_logicamente(self):
        self.activo = False
        self.save()
