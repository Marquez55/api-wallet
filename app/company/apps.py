from django.apps import AppConfig

class CompanyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.company'

    def ready(self):
        # Importa los modelos después de que estén definidos
        import app.company.signals


