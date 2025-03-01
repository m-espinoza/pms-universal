from django.conf import settings
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
        default="PENDING",
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

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name=_("Creado por"),
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Pago")
        verbose_name_plural = _("Pagos")
        ordering = ["-payment_date"]

    def __str__(self):
        return f"Pago {self.id} - Reserva {self.booking.id} - $ {self.amount}"

    def mark_as_completed(self, user):
        """Marca el pago como completado."""
        self.status = "COMPLETED"
        self.save()

        # Si el pago es en efectivo, registrarlo en la caja
        if self.payment_method == "CASH" and self.status == "COMPLETED":
            CashRegisterEntry.objects.create(
                payment=self,
                entry_type="DEPOSIT",
                amount=self.amount,
                description=f"Pago en efectivo de reserva #{self.booking.id}",
            )

    def refund(self, amount=None, user=None):
        """
        Reembolsa el pago completo o parcialmente.

        Args:
            amount (Decimal, optional):
            Monto a reembolsar. Si no se especifica,
            se reembolsa el monto completo.
            user (User): Usuario que realiza el reembolso
        """
        if amount and amount > self.amount:
            raise ValueError(
                _(
                    "El monto a reembolsar no puede ser mayor que el monto del pago"  # noqa
                )
            )

        refund_amount = amount if amount else self.amount

        if amount:
            self.status = "PARTIALLY_REFUNDED"
        else:
            self.status = "REFUNDED"

        self.save()

        # Si el reembolso es de un pago en efectivo, registrar salida de caja
        if self.payment_method == "CASH":
            CashRegisterEntry.objects.create(
                payment=self,
                entry_type="WITHDRAWAL",
                amount=refund_amount,
                description=f"Reembolso en efectivo de reserva #{self.booking.id}",  # noqa
            )

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

        # Guarda el pago
        super().save(*args, **kwargs)

        # Si es un pago nuevo en efectivo
        # y está completado, registrarlo en caja
        if (
            kwargs.get("force_insert", False)
            and self.payment_method == "CASH"
            and self.status == "COMPLETED"
        ):
            CashRegisterEntry.objects.create(
                payment=self,
                entry_type="DEPOSIT",
                amount=self.amount,
                description=f"Pago en efectivo de reserva #{self.booking.id}",
            )


class CashRegisterEntry(models.Model):
    """Modelo para registrar movimientos en la caja."""

    ENTRY_TYPE_CHOICES = [
        ("DEPOSIT", _("Ingreso")),
        ("WITHDRAWAL", _("Retiro")),
    ]

    payment = models.ForeignKey(
        Payment,
        on_delete=models.SET_NULL,
        related_name="cash_entries",
        verbose_name=_("Pago relacionado"),
        null=True,
        blank=True,
    )
    entry_type = models.CharField(
        verbose_name=_("Tipo de movimiento"),
        max_length=20,
        choices=ENTRY_TYPE_CHOICES,  # noqa
    )
    amount = models.DecimalField(
        verbose_name=_("Monto"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )
    description = models.TextField(verbose_name=_("Descripción"))

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Movimiento de caja")
        verbose_name_plural = _("Movimientos de caja")
        ordering = ["-created_at"]

    def __str__(self):
        entry_type_display = (
            "Ingreso" if self.entry_type == "DEPOSIT" else "Retiro"
        )  # noqa
        return f"{entry_type_display} de ${self.amount} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"  # noqa

    def clean(self):
        """Valida que haya suficiente saldo para retiros."""
        if self.entry_type == "WITHDRAWAL" and not self.pk:
            current_balance = self.get_current_balance()
            if self.amount > current_balance:
                raise ValidationError(
                    _(
                        f"No hay suficiente saldo en caja. Saldo actual: ${current_balance}"  # noqa
                    )
                )

        super().clean()

    def save(self, *args, **kwargs):
        """Asegura que se ejecute la validación antes de guardar."""
        self.full_clean()
        super().save(*args, **kwargs)

    @staticmethod
    def get_current_balance():
        """Calcula el saldo actual de la caja."""
        deposits = (
            CashRegisterEntry.objects.filter(entry_type="DEPOSIT").aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        withdrawals = (
            CashRegisterEntry.objects.filter(entry_type="WITHDRAWAL").aggregate(  # noqa
                total=Sum("amount")
            )["total"]
            or 0
        )

        return deposits - withdrawals
