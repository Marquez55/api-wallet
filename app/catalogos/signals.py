from django.db.models.signals import post_migrate
from django.dispatch import receiver



@receiver(post_migrate)
def create_catalog(sender, **kwargs):


    if Anios.objects.count() == 0:
        # Crear años si no existen
        Anios.objects.create(anio=2024, activo=True)
        Anios.objects.create(anio=2025, activo=True)
        Anios.objects.create(anio=2026, activo=True)
        Anios.objects.create(anio=2027, activo=True)
        Anios.objects.create(anio=2028, activo=True)
        Anios.objects.create(anio=2029, activo=True)
        Anios.objects.create(anio=2030, activo=True)
        Anios.objects.create(anio=2031, activo=True)
        Anios.objects.create(anio=2032, activo=True)
        Anios.objects.create(anio=2033, activo=True)

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
        Tipo.objects.create(tipo='Transferencia', activo=True)
        Tipo.objects.create(tipo='Ajuste', activo=True)
        Tipo.objects.create(tipo='Otro', activo=True)