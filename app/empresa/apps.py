from django.apps import AppConfig

class EmpresaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.empresa'

    def ready(self):
        # Importa los modelos después de que estén definidos
        import app.empresa.signals