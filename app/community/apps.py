from django.apps import AppConfig


class CommunityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.community'


    def ready(self):
        import app.community.signals  # Import signals module when app is ready
