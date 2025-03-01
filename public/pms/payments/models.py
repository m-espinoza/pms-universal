from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _

from bookings.models import Booking


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
        return f"Pago {self.id} - Reserva {self.booking.id} - $ {self.amount}"

    def mark_as_completed(self):
        """Marca el pago como completado."""
        self.status = "COMPLETED"
        self.save()

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

    def clean(self):
        """
        Valida que el monto del pago no exceda
        la deuda pendiente de la reserva.
        Si el pago excede la deuda, lanza una ValidationError.
        """

        # Solo validamos si es un objeto nuevo (sin ID asignado)
        # y si el estado no es 'REFUNDED' (para permitir reembolsos)
        if not self.pk and self.status != "REFUNDED":
            # Obtenemos el total de pagos completados
            total_paid = (
                self.booking.payments.filter(status="COMPLETED").aggregate(
                    total=Sum("amount")
                )["total"]
                or 0.00
            )

            # Calculamos la deuda pendiente
            pending_debt = self.booking.total_price - float(total_paid)

            # Si el pago es mayor que la deuda pendiente
            if self.amount > pending_debt:
                excess_amount = float(self.amount) - pending_debt
                raise ValidationError(
                    f"El pago excede la deuda pendiente por {excess_amount}. "
                    f"La deuda pendiente es de {pending_debt}."
                )

        super().clean()

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para asegurar que se ejecuta la validación.
        """
        self.full_clean()
        super().save(*args, **kwargs)
