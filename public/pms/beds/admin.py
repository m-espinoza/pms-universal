from django.contrib import admin
from .models import Room, Bed  # Importa tus modelos


# Registra los modelos en el panel de administración
admin.site.register(Room)
admin.site.register(Bed)