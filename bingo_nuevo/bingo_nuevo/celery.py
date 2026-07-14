import os
from celery import Celery

# Establece el módulo de configuración de Django por defecto para Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bingo_nuevo.settings')

# Crea la instancia de Celery
app = Celery('bingo_nuevo')

# Carga la configuración usando prefijos 'CELERY_' en tu settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodescubre tareas asíncronas (buscará archivos tasks.py en tus apps)
app.autodiscover_tasks()