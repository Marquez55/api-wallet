from django.apps import AppConfig


class catalogsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.catalogos'

    def ready(self):
        import app.catalogos.signals