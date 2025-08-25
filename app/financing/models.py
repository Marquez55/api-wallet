from django.db import models
from django.contrib.auth.models import User
from datetime import date
import calendar

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


class ConceptoPrestamo(models.Model):
    prestamo = models.ForeignKey(Prestamo, on_delete=models.CASCADE, related_name='conceptos')
    descripcion = models.CharField(max_length=300)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.descripcion} — ${self.monto:,.2f} ({self.fecha.strftime('%d/%m/%Y')})"

    def eliminar_logicamente(self):
        self.activo = False
        self.save()
        
        
        
        
        
class CardCredito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=300)
    limite = models.DecimalField(max_digits=12, decimal_places=2)
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    tasa_interes = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # % anual
    fecha_corte = models.DateField()  # se interpreta como “día del mes” (año canónico)
    fecha_pago  = models.DateField()  # se interpreta como “día del mes” (año canónico)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} — Límite: ${self.limite:,.2f}, Saldo: ${self.saldo:,.2f}"

    def eliminar_logicamente(self):
        self.activo = False
        self.save()

    # ---------- utilidades de ciclo ----------
    @property
    def dia_corte(self) -> int:
        return self.fecha_corte.day

    @property
    def dia_pago(self) -> int:
        return self.fecha_pago.day

    @staticmethod
    def _clamp_day(year:int, month:int, day:int) -> int:
        return min(day, calendar.monthrange(year, month)[1])

    @classmethod
    def _next_occurrence(cls, day:int, ref:date) -> date:
        y, m = ref.year, ref.month
        d = cls._clamp_day(y, m, day)
        cand = date(y, m, d)
        if cand >= ref:
            return cand
        y2, m2 = (y + 1, 1) if m == 12 else (y, m + 1)
        return date(y2, m2, cls._clamp_day(y2, m2, day))

    def proximas_fechas(self, ref:date|None=None) -> dict:
        ref = ref or date.today()
        corte_actual = self._next_occurrence(self.dia_corte, ref)

        y, m = corte_actual.year, corte_actual.month
        if self.dia_pago <= self.dia_corte:
            y2, m2 = (y + 1, 1) if m == 12 else (y, m + 1)
            pago = date(y2, m2, self._clamp_day(y2, m2, self.dia_pago))
        else:
            pago = date(y, m, self._clamp_day(y, m, self.dia_pago))

        return {"corte_actual": corte_actual, "pago_actual": pago}
        
class ComprasTarjetaCredito(models.Model):
    tarjeta_credito = models.ForeignKey(CardCredito, on_delete=models.CASCADE, related_name='compras')
    descripcion = models.CharField(max_length=300)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_compra = models.DateField()
    meses = models.PositiveIntegerField(default=1)
    msi = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.descripcion} — ${self.monto:,.2f} ({self.fecha_compra.strftime('%d/%m/%Y')})"

    def eliminar_logicamente(self):
        self.activo = False
        self.save()
        
class PagoTarjetaCredito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tarjeta_credito = models.ForeignKey(CardCredito, on_delete=models.CASCADE, related_name='pagos')
    pago_compras = models.ManyToManyField(ComprasTarjetaCredito, related_name='pagos_tarjeta')
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_pago = models.DateField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.tarjeta_credito.nombre} — Pago: ${self.monto:,.2f} ({self.fecha_pago.strftime('%d/%m/%Y')})"

    def eliminar_logicamente(self):
        self.activo = False
        self.save()