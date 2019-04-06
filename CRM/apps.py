from django.apps import AppConfig


class CrmConfig(AppConfig):
    name = 'CRM'

    def ready(self):
        import CRM.signals