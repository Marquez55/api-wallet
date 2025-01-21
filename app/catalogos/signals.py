from django.db.models.signals import post_migrate
from django.dispatch import receiver
from app.catalogos.models import Mes, Tipo, TipoIngreso



@receiver(post_migrate)
def create_catalog(sender, **kwargs):


    if Mes.objects.count() == 0:
        # Crear meses si no existen
        Mes.objects.create(mes='Enero', activo=True)
        Mes.objects.create(mes='Febrero', activo=True)
        Mes.objects.create(mes='Marzo', activo=True)
        Mes.objects.create(mes='Abril', activo=True)
        Mes.objects.create(mes='Mayo', activo=True)
        Mes.objects.create(mes='Junio', activo=True)
        Mes.objects.create(mes='Julio', activo=True)
        Mes.objects.create(mes='Agosto', activo=True)
        Mes.objects.create(mes='Septiembre', activo=True)
        Mes.objects.create(mes='Octubre', activo=True)
        Mes.objects.create(mes='Noviembre', activo=True)
        Mes.objects.create(mes='Diciembre', activo=True)


    if Tipo.objects.count() == 0:
        # Crear tipos si no existen
        Tipo.objects.create(tipo='Ingreso', activo=True)
        Tipo.objects.create(tipo='Egreso', activo=True)


    if TipoIngreso.objects.count() == 0:
        # Crear tipos si no existen
        TipoIngreso.objects.create(ingreso='Salario', activo=True)
        TipoIngreso.objects.create(ingreso='Primera Quincena', activo=True)
        TipoIngreso.objects.create(ingreso='Segunda Quincena', activo=True)
        TipoIngreso.objects.create(ingreso='Otro', activo=True)
