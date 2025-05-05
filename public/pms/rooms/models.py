from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

class Property(models.Model):
    PROPERTY_TYPES = [
        ("HOTEL", _("Hotel")),
        ("HOSTEL", _("Hostal/Albergue")),
        ("CAMPING", _("Camping")),
        ("RESORT", _("Resort/Complejo turístico")),
        ("APARTMENT", _("Hotel apartamento/Apart-hotel")),
        ("BNB", _("Bed and Breakfast")),
        ("GUESTHOUSE", _("Casa de huéspedes")),
        ("BOUTIQUE", _("Hotel boutique")),
        ("ECOLODGE", _("Eco-lodge/Alojamiento ecológico")),
        ("VACATION_RENTAL", _("Alquiler vacacional")),
        ("GLAMPING", _("Glamping")),
        ("OTHER", _("Otro tipo de alojamiento")),
    ]

    name = models.CharField(
        max_length=128,
        verbose_name=_("Nombre"),
        help_text=_("El nombre de la propiedad debe ser único."),
        unique=True,
    )

    property_type = models.CharField(
        max_length=32, 
        choices=PROPERTY_TYPES, 
        verbose_name=_("Tipo de propiedad")
    )

    description = models.TextField(
        blank=True,
        verbose_name=_("Descripción"),
        help_text=_("Descripción general de la propiedad"),
    )

    address = models.TextField(
        blank=True,
        verbose_name=_("Dirección"),
        help_text=_("Dirección física de la propiedad"),
    )

    is_active = models.BooleanField(default=True, verbose_name=_("Activo")) # noqa

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Propiedad")
        verbose_name_plural = _("Propiedades")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_property_type_display()})" # noqa

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

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="rooms",
        verbose_name=_("Propiedad"),
    )

    name = models.CharField(
        max_length=128,
        verbose_name=_("Nombre"),
        help_text=_("El nombre de la habitación debe ser único dentro de la propiedad.") # noqa
    )

    room_type = models.CharField(
        max_length=32, choices=ROOM_TYPES, verbose_name=_("Tipo de habitación") # noqa
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
        unique_together = ["property", "name"] 

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
        default="SINGLE_BED",
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


class Plan(models.Model):
    name = models.CharField(
        max_length=128,
        verbose_name=_("Nombre"),
        help_text=_("El nombre del plan debe ser único."),
        unique=True,
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="plans",
        verbose_name=_("Habitación"),
    )

    start_date = models.DateField(verbose_name=_("Fecha inicio"))

    end_date = models.DateField(verbose_name=_("Fecha fin"))

    description = models.TextField(
        blank=True,
        verbose_name=_("Descripción"),
        help_text=_("Descripción del plan (incluye, no incluye, etc.)"),
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name=_("Precio"),
    )

    is_active = models.BooleanField(default=True, verbose_name=_("Activo"))

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Plan")
        verbose_name_plural = _("Planes")
        ordering = ["name"]

    @staticmethod
    def _get_active_plan(unit, start_date, end_date):
        if not unit.room or not start_date or not end_date:
            return None

        return Plan.objects.filter(
            room=unit.room,
            start_date__lte=end_date,
            end_date__gte=start_date,
            is_active=True,
        ).first()

    @staticmethod
    def get_price_room(unit, start_date, end_date):
        # Use the helper method to get the active plan
        plan = Plan._get_active_plan(unit, start_date, end_date)

        # Return the plan's price if found, otherwise the room's base price
        return plan.price if plan else unit.room.base_price

    @staticmethod
    def get_total_price(unit, start_date, end_date):
        # Calculate the number of days in the reservation
        num_days = (end_date - start_date).days + 1  # Include the start date

        # Use the helper method to get the active plan
        plan = Plan._get_active_plan(unit, start_date, end_date)

        # Determine the price per day (use plan price
        # if available, otherwise room base price)
        price_per_day = plan.price if plan else unit.room.base_price

        # Calculate and return the total price for the reservation
        total_price = price_per_day * num_days
        return total_price

    def clean(self):
        """Validaciones personalizadas para el plan"""
        # Primero validar campos obligatorios
        if not self.room:
            raise ValidationError(
                {"room": _("El plan debe estar asociado a una habitación")}
            )

        if self.start_date is None or self.end_date is None:
            raise ValidationError(
                {"start_date": _("La fecha de inicio y fin son obligatorias")}
            )

        # Luego validar relaciones entre fechas
        if self.start_date > self.end_date:
            raise ValidationError(
                {
                    "start_date": _(
                        "La fecha de inicio debe ser anterior a la fecha de fin"  # noqa
                    )
                }  # noqa
            )

        # Solo entonces verificar solapamiento
        overlapping_plans = Plan.objects.filter(
            room=self.room,
            is_active=True,
            start_date__lte=self.end_date,
            end_date__gte=self.start_date,
        ).exclude(
            pk=self.pk
        )  # Excluir el propio plan si ya existe

        if overlapping_plans.exists():
            raise ValidationError(
                {"start_date": _("El plan se superpone con otro plan activo")}
            )

        if self.price <= 0:
            raise ValidationError({"price": _("El precio debe ser mayor a 0")})

    def __str__(self):
        return f"{_('Plan')} {self.name} (${self.price:.2f})"
