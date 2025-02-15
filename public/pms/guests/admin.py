from django.contrib import admin
from .models import Guest  # Importa el modelo

# Registra el modelo en el panel de administración
admin.site.register(Guest)