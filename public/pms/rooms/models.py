from django.db import models
from django.utils.translation import gettext_lazy as _


class Room(models.Model):
    ROOM_TYPES = [
        ("CABIN", _("Cabaña")),
        ("DORM", _("Dormitorio compartido")),
        ("GLAMPING", _("Glamping")),
        ("CAMPING", _("Zona de camping")),
        ("PRIVATE_ROOM", _("Habitación privada")),
        ("SPECIAL_ROOM", _("Dormitorio especial")),
        ("APARTMENT", _("Apartamento")),
        ("VILLA", _("Villa")),
        ("TENT", _("Tienda de campaña preparada")),
        ("OTHER", _("Otro tipo de alojamiento")),
    ]

    name = models.CharField(
        max_length=128,
        verbose_name=_("Nombre"),
        help_text=_("El nombre de la habitación debe ser único."),
        unique=True,
    )

    room_type = models.CharField(
        max_length=32, choices=ROOM_TYPES, verbose_name=_("Tipo de habitación")
    )

    capacity = models.IntegerField(
        verbose_name=_("Capacidad"), blank=True, default=1
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
        # Unidades para cabañas
        ("BASIC_CABIN", _("Cabaña básica")),
        ("DELUXE_CABIN", _("Cabaña deluxe")),
        # Unidades para dormitorios compartidos
        ("SINGLE_BED", _("Cama individual")),
        ("BUNK_BED", _("Litera")),
        ("QUEEN_BED", _("Cama queen")),
        ("KING_BED", _("Cama king")),
        # Unidades para glamping
        ("GLAMPING_TENT", _("Tienda de glamping")),
        ("GLAMPING_POD", _("Cápsula de glamping")),
        # Unidades para camping
        ("TENT_SPACE", _("Espacio para tienda")),
        ("CAMPER_SPACE", _("Espacio para caravana")),
        ("HAMMOCK", _("Hamaca")),
        # Unidades para habitaciones privadas
        ("PRIVATE_ROOM", _("Habitación privada")),
        ("PRIVATE_SUITE", _("Suite privada")),
        # Unidades para dormitorios especiales
        ("SPECIAL_BED", _("Cama especial")),
        ("SPECIAL_ROOM", _("Habitación especial")),
        # Unidades para apartamentos y villas
        ("STUDIO", _("Estudio")),
        ("ONE_BEDROOM", _("Una habitación")),
        ("TWO_BEDROOM", _("Dos habitaciones")),
        ("ENTIRE_APARTMENT", _("Apartamento completo")),
        ("ENTIRE_VILLA", _("Villa completa")),
        # Otras unidades
        ("AIRSTREAM", _("Airstream")),
        ("TEEPEE", _("Tipi")),
        ("YURT", _("Yurta")),
        ("TREEHOUSE", _("Casa en el árbol")),
        ("OTHER", _("Otra unidad")),  # Para unidades no especificadas
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
