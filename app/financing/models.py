from django.db import models
from django.contrib.auth.models import User


class Prestamo(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=300)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} — ${self.monto:,.2f}"

    def eliminar_logicamente(self):
        self.activo = False
        self.save()


class PagosPrestamo(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    prestamo = models.ForeignKey(Prestamo, on_delete=models.CASCADE, related_name='pagos')
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_pago = models.DateField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.prestamo.nombre} — ${self.monto:,.2f} ({self.fecha_pago.strftime('%d/%m/%Y')})"

    def eliminar_logicamente(self):
        self.activo = False
        self.save()
