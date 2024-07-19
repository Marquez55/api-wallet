from django.apps import AppConfig


class CatalogosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.catalogos'

    def ready(self):
        # Importa los modelos después de que estén definidos
        import app.catalogos.signals