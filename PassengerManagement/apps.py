from django.apps import AppConfig


class PassengermanagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'PassengerManagement'

    def ready(self):
        import PassengerManagement.signals
