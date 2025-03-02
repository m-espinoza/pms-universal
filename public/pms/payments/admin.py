from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import CashRegisterEntry, Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin para el modelo de Pagos."""

    list_display = (
        "id",
        "booking_info",
        "payment_type",
        "amount",
        "payment_method",
        "status",
        "payment_date",
        "transaction_id",
        "created_by",        
    )
    list_filter = ("payment_method", "status", "payment_date", "payment_type")
    search_fields = ("booking__guest__name", "transaction_id", "notes")
    readonly_fields = ("payment_date", "created_by")  # Hacer created_by de solo lectura
    date_hierarchy = "payment_date"
    actions = ["mark_as_completed", "mark_as_refunded"]

    fieldsets = (
        (None, {"fields": ("booking", "amount", "payment_method", "payment_type")}),
        (
            _("Estado y detalles"),
            {"fields": ("status", "transaction_id", "payment_date")},
        ),
        (
            _("Información adicional"),
            {"fields": ("notes", "created_by"), "classes": ("collapse",)},  # Agregar created_by al fieldset
        ),  # noqa
    )

    def booking_info(self, obj):
        """Muestra información resumida de la reserva."""
        return f"{obj.booking.guest.name} - {obj.booking.check_in_date} a {obj.booking.check_out_date}"  # noqa

    booking_info.short_description = _("Información de reserva")

    def mark_as_completed(self, request, queryset):
        """Acción para marcar múltiples pagos como completados."""
        updated_count = 0
        for payment in queryset:
            if payment.status != "COMPLETED":
                payment.mark_as_completed()
                updated_count += 1

        if updated_count == 1:
            message = _("1 pago ha sido marcado como completado.")
        else:
            message = _("{} pagos han sido marcados como completados.").format(
                updated_count
            )

        self.message_user(request, message)

    mark_as_completed.short_description = _(
        "Marcar pagos seleccionados como completados"
    )

    def mark_as_refunded(self, request, queryset):
        """Acción para marcar múltiples pagos como reembolsados."""
        updated_count = 0
        for payment in queryset:
            if payment.status == "COMPLETED":
                payment.refund()
                updated_count += 1

        if updated_count == 1:
            message = _("1 pago ha sido marcado como reembolsado.")
        else:
            message = _("{} pagos han sido marcados como reembolsados.").format(  # noqa
                updated_count
            )

        self.message_user(request, message)

    mark_as_refunded.short_description = _(
        "Marcar pagos seleccionados como reembolsados"
    )

    def get_queryset(self, request):
        """Optimiza las consultas para reducir el número 
        de consultas a la base de datos."""  # noqa
        return (
            super()
            .get_queryset(request)
            .select_related("booking", "booking__guest", "created_by")  # Incluir created_by en select_related
        )

    def save_model(self, request, obj, form, change):
        """Asigna automáticamente el usuario actual como created_by al crear un pago."""
        if not obj.pk:  # Si es un nuevo pago
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(CashRegisterEntry)
class CashRegisterEntryAdmin(admin.ModelAdmin):
    """Admin para el modelo de movimientos de caja."""

    list_display = (
        "id",
        "entry_type_display",
        "amount",
        "description",
        "created_at",
        "payment_info",
    )
    list_filter = ("entry_type", "created_at")
    search_fields = ("description", "payment__booking__guest__name")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
    actions = ["mark_as_deposit", "mark_as_withdrawal"]

    fieldsets = (
        (None, {"fields": ("payment", "entry_type", "amount")}),
        (
            _("Información adicional"),
            {"fields": ("description", "created_at", "updated_at")},
        ),
    )

    def entry_type_display(self, obj):
        """Muestra el tipo de movimiento de forma legible."""
        return "Ingreso" if obj.entry_type == "DEPOSIT" else "Retiro"

    entry_type_display.short_description = _("Tipo de movimiento")

    def payment_info(self, obj):
        """Muestra información resumida del pago relacionado."""
        if obj.payment:
            return f"Pago #{obj.payment.id} - {obj.payment.booking.guest.name}"
        return "Sin pago relacionado"

    payment_info.short_description = _("Información del pago")

    def mark_as_deposit(self, request, queryset):
        """Acción para marcar múltiples movimientos como ingresos."""
        updated_count = queryset.update(entry_type="DEPOSIT")

        if updated_count == 1:
            message = _("1 movimiento ha sido marcado como ingreso.")
        else:
            message = _("{} movimientos han sido marcados como ingresos.").format(
                updated_count
            )

        self.message_user(request, message)

    mark_as_deposit.short_description = _(
        "Marcar movimientos seleccionados como ingresos"
    )

    def mark_as_withdrawal(self, request, queryset):
        """Acción para marcar múltiples movimientos como retiros."""
        updated_count = queryset.update(entry_type="WITHDRAWAL")

        if updated_count == 1:
            message = _("1 movimiento ha sido marcado como retiro.")
        else:
            message = _("{} movimientos han sido marcados como retiros.").format(
                updated_count
            )

        self.message_user(request, message)

    mark_as_withdrawal.short_description = _(
        "Marcar movimientos seleccionados como retiros"
    )

    def get_queryset(self, request):
        """Optimiza las consultas para reducir el número 
        de consultas a la base de datos."""  # noqa
        return (
            super()
            .get_queryset(request)
            .select_related("payment", "payment__booking", "payment__booking__guest")  # noqa
        )