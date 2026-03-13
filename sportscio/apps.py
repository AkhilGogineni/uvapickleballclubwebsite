from django.apps import AppConfig


class SportscioConfig(AppConfig):
    name = 'sportscio'
    
    def ready(self):
        import sportscio.signals
