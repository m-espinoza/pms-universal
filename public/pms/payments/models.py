from bookings.models import Booking
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Payment(models.Model):
    """Modelo para gestionar los pagos de reservas en el hostel."""

    PAYMENT_METHOD_CHOICES = [
        ("CASH", _("Efectivo")),
        ("CREDIT_CARD", _("Tarjeta de crédito")),
        ("DEBIT_CARD", _("Tarjeta de débito")),
        ("BANK_TRANSFER", _("Transferencia bancaria")),
        ("PAYPAL", _("PayPal")),
        ("QR", _("QR")),
        ("OTHER", _("Otro")),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("PENDING", _("Pendiente")),
        ("COMPLETED", _("Completado")),
        ("FAILED", _("Fallido")),
        ("REFUNDED", _("Reembolsado")),
        ("PARTIALLY_REFUNDED", _("Parcialmente reembolsado")),
    ]

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name=_("Reserva"),
    )
    amount = models.DecimalField(
        verbose_name=_("Monto"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )
    payment_date = models.DateTimeField(_("Fecha de pago"), auto_now_add=True)
    payment_method = models.CharField(
        verbose_name=_("Método de pago"),
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default="CASH",
    )
    status = models.CharField(
        verbose_name=_("Estado"),
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="PENDING",  # noqa
    )
    transaction_id = models.CharField(
        verbose_name=_("ID de transacción"),
        max_length=100,
        blank=True,
        null=True,
        help_text=_(
            "Identificador único de la transacción para pagos electrónicos"
        ),  # noqa
    )
    notes = models.TextField(_("Notas"), blank=True, null=True)

    class Meta:
        verbose_name = _("Pago")
        verbose_name_plural = _("Pagos")
        ordering = ["-payment_date"]

    def __str__(self):
        return f"Pago {self.id} - Reserva {self.booking.id} - {self.amount} €"

    def mark_as_completed(self):
        """Marca el pago como completado."""
        self.status = "COMPLETED"
        self.save()

        # Actualizar el estado de la reserva si corresponde
        if (
            self.booking.total_price
            <= self.booking.payments.filter(status="COMPLETED").aggregate(
                models.Sum("amount")
            )["amount__sum"]
        ):
            if self.booking.status == "PENDING_PAYMENT":
                self.booking.confirm_booking()

    def refund(self, amount=None):
        """
        Reembolsa el pago completo o parcialmente.

        Args:
            amount (Decimal, optional):
            Monto a reembolsar. Si no se especifica,
            se reembolsa el monto completo.
        """
        if amount and amount > self.amount:
            raise ValueError(
                _(
                    "El monto a reembolsar no puede ser mayor que el monto del pago"  # noqa
                )  # noqa
            )

        if amount:
            self.status = "PARTIALLY_REFUNDED"
            # Aquí podrías crear un nuevo registro de reembolso si es necesario
        else:
            self.status = "REFUNDED"

        self.save()
