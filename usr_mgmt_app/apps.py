from django.apps import AppConfig


class UsrMgmtAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usr_mgmt_app'

    def ready(self):
        import usr_mgmt_app.signals  # Ensure signals are loaded

