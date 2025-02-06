from django.db import models
from django.core.validators import MinValueValidator, DecimalValidator

class Room(models.Model):
    name = models.CharField(max_length=50, verbose_name="Nombre de la habitación")
    description = models.TextField(
        verbose_name="Descripción",
        help_text="Características de la habitación (baño privado, amenities, etc.)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Habitación"
        verbose_name_plural = "Habitaciones"
        ordering = ['name']

    def __str__(self):
        return self.name

class BedCategory(models.Model):
    name = models.CharField(max_length=50, verbose_name="Nombre de la categoría")
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Precio por noche"
    )
    description = models.TextField(
        verbose_name="Descripción",
        help_text="Incluir dimensiones y características de la cama"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Categoría de cama"
        verbose_name_plural = "Categorías de camas"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - ${self.price_per_night}/noche"

class Bed(models.Model):
    STATES = [
        ('enabled', 'Habilitada'),
        ('disabled', 'Deshabilitada'),
        ('maintenance', 'En Mantenimiento'),
    ]
    
    name = models.CharField(max_length=50, verbose_name="Nombre de la cama")
    bed_number = models.CharField(max_length=10, verbose_name="Número de cama")
    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name='beds',
        verbose_name="Habitación"
    )
    category = models.ForeignKey(
        BedCategory,
        on_delete=models.PROTECT,
        related_name='beds',
        verbose_name="Categoría"
    )
    capacity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        default=1,
        verbose_name="Capacidad de personas"
    )
    status = models.CharField(
        max_length=20,
        choices=STATES,
        default='enabled',
        verbose_name="Estado"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cama"
        verbose_name_plural = "Camas"
        ordering = ['room', 'bed_number']
        unique_together = ['room', 'bed_number']

    def __str__(self):
        return f"{self.room} - Cama {self.bed_number} ({self.category.name})"