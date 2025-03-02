from datetime import date

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, Sum
from django.utils.translation import gettext_lazy as _

from beds.models import Bed
from guests.models import Guest


class Booking(models.Model):
    STATUS_CHOICES = [
        ("PENDING", _("Pendiente")),  # Reserva inicial, esperando confirmación
        ("CONFIRMED", _("Confirmada")),  # Reserva confirmada
        ("CHECKED_IN", _("Registrado")),  # Huésped ya está en el hostel
        ("CHECKED_OUT", _("Salida")),  # Huésped ya se fue
        ("CANCELLED", _("Cancelada")),  # Reserva cancelada
    ]

    guest = models.ForeignKey(
        Guest,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name=_("Huésped"),
    )

    bed = models.ForeignKey(
        Bed,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name=_("Cama"),  # noqa
    )

    check_in_date = models.DateField(verbose_name=_("Fecha de entrada"))

    check_out_date = models.DateField(verbose_name=_("Fecha de salida"))

    status = models.CharField(
        max_length=11,
        choices=STATUS_CHOICES,
        default="PENDING",
        verbose_name=_("Estado"),
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Precio total")
    )

    notes = models.TextField(blank=True, verbose_name=_("Notas"))

    class Meta:
        verbose_name = _("Reserva")
        verbose_name_plural = _("Reservas")
        # Índices para mejorar el rendimiento de las búsquedas
        indexes = [
            models.Index(fields=["bed", "check_in_date", "check_out_date"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.guest} - {self.bed} ({self.check_in_date} to {self.check_out_date})"  # noqa

    def clean(self):
        """Validaciones personalizadas para la reserva"""
        if not self.check_in_date or not self.check_out_date:
            return

        # Validar que check_in sea anterior a check_out
        if self.check_in_date >= self.check_out_date:
            raise ValidationError(
                {
                    "check_in_date": _(
                        "La fecha de entrada debe ser anterior a la fecha de salida"  # noqa
                    )  # noqa
                }
            )

        # Validar que check_in no sea en el pasado
        if self.check_in_date < date.today():
            raise ValidationError(
                {"check_in_date": _("No se pueden crear reservas en el pasado")}  # noqa
            )

        # Validar disponibilidad de la cama
        if not self.is_bed_available():
            raise ValidationError(
                _("Esta cama no está disponible para las fechas seleccionadas")
            )  # noqa

    def is_bed_available(self):
        """
        Verifica si la cama está disponible para las fechas seleccionadas
        """
        overlapping_bookings = Booking.objects.filter(
            bed=self.bed,
            status__in=["PENDING", "CONFIRMED", "CHECKED_IN"],
        ).filter(
            # Busca superposición de fechas
            Q(check_in_date__lt=self.check_out_date)
            & Q(check_out_date__gt=self.check_in_date)
        )

        # Excluir la reserva actual (importante para actualizaciones)
        if self.pk:
            overlapping_bookings = overlapping_bookings.exclude(pk=self.pk)

        return not overlapping_bookings.exists()

    def save(self, *args, **kwargs):
        self.clean()  # Ejecutar validaciones antes de guardar
        if not self.total_price:
            # Calcular el precio total si no está establecido
            nights = (self.check_out_date - self.check_in_date).days
            self.total_price = self.bed.base_price * nights
        super().save(*args, **kwargs)

    def confirm_booking(self):
        """Confirma una reserva pendiente"""
        if self.status != "PENDING":
            raise ValidationError(
                _("Solo se pueden confirmar reservas pendientes")  # noqa
            )
        self.status = "CONFIRMED"
        self.save()

    def check_in(self):
        """Realiza el check-in de una reserva confirmada"""
        if self.status != "CONFIRMED":
            raise ValidationError(
                _("Solo se pueden registrar reservas confirmadas")
            )  # noqa
        self.status = "CHECKED_IN"
        self.save()

    def check_out(self):
        """Realiza el check-out de una reserva con check-in"""
        if self.status != "CHECKED_IN":
            raise ValidationError(
                _("Solo se pueden dar de baja reservas registradas")
            )  # noqa
        self.status = "CHECKED_OUT"
        self.save()

    def cancel(self):
        """Cancela una reserva pendiente o confirmada"""
        if self.status not in ["PENDING", "CONFIRMED"]:
            raise ValidationError(
                _("Solo se pueden cancelar reservas pendientes o confirmadas")
            )
        self.status = "CANCELLED"
        self.save()

    def get_payment_status(self):
        """
        Determina el estado de pago de la reserva.

        Returns:
            str: Estado de pago: 'NO_PAYMENT' (sin pagos),
                'PARTIAL_PAYMENT' (pagos parciales),
                o 'FULLY_PAID' (pagado completamente)
        """

        # Obtenemos la suma de todos los pagos completados
        payments_sum = (
            self.payments.filter(status="COMPLETED").aggregate(
                total=Sum("amount")
            )[  # noqa
                "total"
            ]
            or 0
        )

        if payments_sum == 0:
            return "NO_PAYMENT"  # No hay pagos
        elif payments_sum < self.total_price:
            return "PARTIAL_PAYMENT"  # Pago parcial
        else:
            return "FULLY_PAID"  # Completamente pagado
