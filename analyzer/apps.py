# analyzer/apps.py
from django.apps import AppConfig

class AnalyzerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analyzer'

    def ready(self):
        import analyzer.signals
        from .scheduler import PriceScraperScheduler
        scheduler = PriceScraperScheduler()
        scheduler.start()