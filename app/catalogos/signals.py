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


