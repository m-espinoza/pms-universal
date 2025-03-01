from datetime import date

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, Sum
from django.utils.translation import gettext_lazy as _

from beds.models import Bed
from guests.models import Guest


class Booking(models.Model):
    STATUS_CHOICES = [
        ("PENDING", _("Pending")),  # Reserva inicial, esperando confirmación
        ("CONFIRMED", _("Confirmed")),  # Reserva confirmada
        ("CHECKED_IN", _("Checked in")),  # Huésped ya está en el hostel
        ("CHECKED_OUT", _("Checked out")),  # Huésped ya se fue
        ("CANCELLED", _("Cancelled")),  # Reserva cancelada
    ]

    guest = models.ForeignKey(
        Guest,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name=_("guest"),
    )

    bed = models.ForeignKey(
        Bed,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name=_("bed"),  # noqa
    )

    check_in_date = models.DateField(verbose_name=_("check-in date"))

    check_out_date = models.DateField(verbose_name=_("check-out date"))

    status = models.CharField(
        max_length=11,
        choices=STATUS_CHOICES,
        default="PENDING",
        verbose_name=_("status"),
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("total price")
    )

    notes = models.TextField(blank=True, verbose_name=_("notes"))

    class Meta:
        verbose_name = _("booking")
        verbose_name_plural = _("bookings")
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
                        "Check-in date must be before check-out date"
                    )  # noqa
                }
            )

        # Validar que check_in no sea en el pasado
        if self.check_in_date < date.today():
            raise ValidationError(
                {"check_in_date": _("Cannot create bookings in the past")}
            )

        # Validar disponibilidad de la cama
        if not self.is_bed_available():
            raise ValidationError(
                _("This bed is not available for the selected dates")
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
            raise ValidationError(_("Only pending bookings can be confirmed"))
        self.status = "CONFIRMED"
        self.save()

    def check_in(self):
        """Realiza el check-in de una reserva confirmada"""
        if self.status != "CONFIRMED":
            raise ValidationError(
                _("Only confirmed bookings can be checked in")
            )  # noqa
        self.status = "CHECKED_IN"
        self.save()

    def check_out(self):
        """Realiza el check-out de una reserva con check-in"""
        if self.status != "CHECKED_IN":
            raise ValidationError(
                _("Only checked-in bookings can be checked out")
            )  # noqa
        self.status = "CHECKED_OUT"
        self.save()

    def cancel(self):
        """Cancela una reserva pendiente o confirmada"""
        if self.status not in ["PENDING", "CONFIRMED"]:
            raise ValidationError(
                _("Only pending or confirmed bookings can be cancelled")
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
            self.payments.filter(status="COMPLETED").aggregate(total=Sum("amount"))[
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
