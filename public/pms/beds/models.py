from django.db import models
from django.utils.translation import gettext_lazy as _


class Room(models.Model):
    ROOM_TYPES = [
        ("DORM", _("Dormitorio")),
        ("PRIVATE", _("Habitación privada")),
    ]

    name = models.CharField(
        max_length=50,
        verbose_name=_("Nombre"),
        help_text=_("El nombre de la habitación debe ser único."),
        unique=True,
    )

    room_type = models.CharField(
        max_length=7, choices=ROOM_TYPES, verbose_name=_("Tipo de habitación")
    )

    capacity = models.IntegerField(
        verbose_name=_("Capacidad"), blank=True, default=1
    )  # noqa

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


class Bed(models.Model):
    BED_TYPES = [
        ("SINGLE", _("Cama Individual")),
        ("BUNK_TOP", _("Litera Superior")),
        ("BUNK_BOTTOM", _("Litera Inferior")),
        ("DOUBLE", _("Cama Doble")),
    ]

    number = models.IntegerField(
        verbose_name=_("Número"),
        null=True,
        blank=True,
    )

    bed_type = models.CharField(
        max_length=11,
        choices=BED_TYPES,
        verbose_name=_("Tipo de cama"),
        default="SINGLE",
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="beds",
        verbose_name=_("Habitación"),
    )

    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name=_("Precio base"),
    )

    is_active = models.BooleanField(default=True, verbose_name=_("Activo"))

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Cama")
        verbose_name_plural = _("Camas")
        unique_together = ["room", "number"]
