from django.db import models
from django.utils.translation import gettext_lazy as _


class Room(models.Model):
    ROOM_TYPES = [
        ("DORM", _("Dormitorio compartido")),
        ("PRIVATE", _("Habitación privada")),
        ("CABIN", _("Cabaña")),
        ("APARTMENT", _("Apartamento")),
        ("STUDIO", _("Estudio")),
        ("SUITE", _("Suite")),
        ("DELUXE", _("Habitación deluxe")),
        ("BUNGALOW", _("Bungalow")),
        ("VILLA", _("Villa")),
        ("COTTAGE", _("Casa rural")),
        ("CAMPING", _("Zona de camping")),
        ("GLAMPING", _("Glamping")),
        ("LOFT", _("Loft")),
        ("MOBILE_HOME", _("Casa móvil")),
        ("TENT", _("Tienda de campaña preparada")),
        ("IGLOO", _("Iglú")),
        ("TREEHOUSE", _("Casa en el árbol")),
        ("YURT", _("Yurta")),
        ("TINY_HOUSE", _("Casa pequeña")),
        ("RV_SPOT", _("Espacio para autocaravana")),
        ("DORM_FEMALE", _("Dormitorio femenino")),
        ("DORM_MALE", _("Dormitorio masculino")),
        ("DORM_MIXED", _("Dormitorio mixto")),
        ("FAMILY_ROOM", _("Habitación familiar")),
    ]

    name = models.CharField(
        max_length=128,
        verbose_name=_("Nombre"),
        help_text=_("El nombre de la habitación debe ser único."),
        unique=True,
    )

    room_type = models.CharField(
        max_length=32,
        choices=ROOM_TYPES,
        verbose_name=_("Tipo de habitación")
    )

    capacity = models.IntegerField(
        verbose_name=_("Capacidad"),
        blank=True,
        default=1
    )  # noqa

    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name=_("Precio base"),
    )

    description = models.TextField(
        blank=True,
        verbose_name=_("Descripción"),
        help_text=_(
            "Descripción de la habitación (baño privado, comodidades, etc.)"  # noqa
        ),
    )

    is_active = models.BooleanField(default=True, verbose_name=_("Activo"))

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Habitación")
        verbose_name_plural = _("Habitaciones")
        ordering = ["name"]

    def __str__(self):
        return f"{_('Habitación')} {self.name} ({self.get_room_type_display()})"  # noqa


class Unit(models.Model):
    UNIT_TYPES = [
        # Camas en dormitorios
        ("SINGLE_BED", _("Cama individual")),
        ("BUNK_TOP", _("Litera superior")),
        ("BUNK_BOTTOM", _("Litera inferior")),
        ("DOUBLE_BED", _("Cama doble")),
        ("QUEEN_BED", _("Cama queen")),
        ("KING_BED", _("Cama king")),
        
        # Cabañas
        ("BASIC_CABIN", _("Cabaña básica")),
        ("STANDARD_CABIN", _("Cabaña estándar")),
        ("DELUXE_CABIN", _("Cabaña deluxe")),
        
        # Apartamentos
        ("STUDIO_UNIT", _("Unidad estudio")),
        ("ONE_BEDROOM", _("Una habitación")),
        ("TWO_BEDROOM", _("Dos habitaciones")),
        ("PENTHOUSE", _("Ático")),
        
        # Camping
        ("TENT_SPACE", _("Espacio para tienda")),
        ("CAMPER_SPACE", _("Espacio para caravana")),
        ("HAMMOCK", _("Hamaca")),
        
        # Alojamientos especiales
        ("POD", _("Cápsula para dormir")),
        ("HAMMOCK", _("Hamaca")),
        ("TENT_PLATFORM", _("Plataforma para tienda")),
        ("AIRSTREAM", _("Airstream")),
        ("TEEPEE", _("Tipi")),
        
        # Adicionales
        ("ENTIRE_ROOM", _("Habitación completa")),
        ("ENTIRE_CABIN", _("Cabaña completa")),
        ("ENTIRE_VILLA", _("Villa completa")),
        ("ENTIRE_HOUSE", _("Casa completa")),
    ]

    name = models.CharField(
        max_length=128,
        verbose_name=_("Identificacion de unidad"),
        null=True,
        blank=True,
    )

    unit_type = models.CharField(
        max_length=32,
        choices=UNIT_TYPES,
        verbose_name=_("Tipo de cama"),
        default="SINGLE",
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="units",
        verbose_name=_("Habitación"),
    )

    is_active = models.BooleanField(default=True, verbose_name=_("Activo"))

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Unidad")
        verbose_name_plural = _("Unidades")
        unique_together = ["room", "name"]
    
    def __str__(self):
        return f"{_('Unidad')} {self.name} ({self.get_unit_type_display()})"  # noqa
