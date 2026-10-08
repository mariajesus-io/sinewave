from django.apps import AppConfig


# Configuración de la app. Django la encuentra porque "tienda" está en INSTALLED_APPS (settings.py).
class TiendaConfig(AppConfig):
    name = 'tienda'
