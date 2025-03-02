from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _

from bookings.models import Booking


class Payment(models.Model):
    """
    Modelo para gestionar los pagos y reembolsos de reservas en el hostel.
    """

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
        ("REFUND", _("Reembolso")),
    ]

    PAYMENT_TYPE_CHOICES = [
        ("PAYMENT", _("Pago")),
        ("REFUND", _("Reembolso")),
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
    )  # Eliminamos el validador para permitir montos negativos
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
    payment_type = models.CharField(
        verbose_name=_("Tipo de operación"),
        max_length=20,
        choices=PAYMENT_TYPE_CHOICES,
        default="PAYMENT",
    )
    # Campo para relacionar un reembolso con su pago original
    original_payment = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="refunds",
        verbose_name=_("Pago original"),
        null=True,
        blank=True,
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
        operation_type = (
            "Reembolso" if self.payment_type == "REFUND" else "Pago"
        )  # noqa
        return f"{operation_type} {self.id} - Reserva {self.booking.id} - $ {abs(self.amount)}"  # noqa

    def refund(self, amount=None, user=None):
        """
        Reembolsa el pago completo o parcialmente.
        Crea un nuevo pago negativo como registro del reembolso.

        Args:
            amount (Decimal, optional):
                Monto a reembolsar. Si no se especifica,
                se reembolsa el monto completo.
            user (User): Usuario que realiza el reembolso

        Returns:
            Payment: El nuevo objeto de pago creado para el reembolso
        """
        if not amount:
            refund_amount = self.amount
            self.status = "REFUNDED"
        else:
            if amount > self.amount:
                raise ValueError(
                    _(
                        "El monto a reembolsar no puede ser mayor que el monto del pago"  # noqa
                    )  # noqa
                )
            elif amount == self.amount:
                refund_amount = amount
                self.status = "REFUNDED"
            else:
                refund_amount = amount
                self.status = "PARTIALLY_REFUNDED"

        self.save()

        # Crear un nuevo pago negativo para el reembolso
        refund_payment = Payment.objects.create(
            booking=self.booking,
            amount=-abs(refund_amount),  # Asegurar que el monto sea negativo
            payment_method=self.payment_method,
            status="COMPLETED",
            payment_type="REFUND",
            original_payment=self,
            created_by=user,
            notes=f"Reembolso del pago #{self.id}",
        )

        return refund_payment

    def clean(self):
        """
        Valida los montos de pagos y reembolsos.
        """
        # Si es un pago normal (no un reembolso)
        if (
            self.payment_type == "PAYMENT"
            and not self.pk
            and self.status != "REFUNDED"  # noqa
        ):  # noqa
            # Validamos que el monto sea positivo
            if self.amount <= 0:
                raise ValidationError(
                    _("El monto del pago debe ser mayor que cero")
                )  # noqa

            # Obtenemos el total de pagos completados (restando los reembolsos)
            payments = self.booking.payments.filter(status="COMPLETED")
            total_paid = (
                sum([p.amount for p in payments]) if payments.exists() else 0.00  # noqa
            )

            # Calculamos la deuda pendiente
            pending_debt = float(self.booking.total_price) - float(total_paid)

            # Si el pago es mayor que la deuda pendiente
            if self.amount > pending_debt:
                excess_amount = float(self.amount) - pending_debt
                raise ValidationError(
                    f"El pago excede la deuda pendiente por {excess_amount}. "
                    f"La deuda pendiente es de {pending_debt}."
                )

        # Si es un reembolso
        elif self.payment_type == "REFUND":
            # Validamos que el monto sea negativo
            if self.amount >= 0:
                raise ValidationError(
                    _("El monto del reembolso debe ser negativo")
                )  # noqa

            # Verificamos que exista el pago original si se especificó
            if self.original_payment and not self.original_payment.pk:
                raise ValidationError(
                    _("El pago original especificado no existe")
                )  # noqa

        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

        # Si el pago es en efectivo y está completado, registrarlo en caja
        if self.status == "COMPLETED":
            # Determinamos el tipo de entrada en la
            # caja según el tipo de operación
            if self.payment_type == "PAYMENT" and self.payment_method == "CASH":  # noqa
                entry_type = "DEPOSIT"
                description = f"Pago en efectivo de reserva #{self.booking.id}"  # noqa
            elif (
                self.payment_type == "REFUND" and self.payment_method == "CASH"
            ):  # noqa
                entry_type = "WITHDRAWAL"
                description = (
                    f"Reembolso en efectivo de reserva #{self.booking.id}"  # noqa
                )
                if self.original_payment:
                    description += (
                        f" (pago original #{self.original_payment.id})"  # noqa
                    )
            else:
                # Si no es efectivo, no registramos en caja
                return

            # Verificar si ya existe una entrada en la caja para este pago
            if not CashRegisterEntry.objects.filter(payment=self).exists():  # noqa
                CashRegisterEntry.objects.create(
                    payment=self,
                    entry_type=entry_type,
                    amount=abs(self.amount),
                    description=description,
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
        choices=ENTRY_TYPE_CHOICES,
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
