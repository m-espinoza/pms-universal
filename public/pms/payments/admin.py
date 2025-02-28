from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin para el modelo de Pagos."""

    list_display = (
        "id",
        "booking_info",
        "amount",
        "payment_method",
        "status",
        "payment_date",
        "transaction_id",
    )
    list_filter = ("payment_method", "status", "payment_date")
    search_fields = ("booking__guest__name", "transaction_id", "notes")
    readonly_fields = ("payment_date",)
    date_hierarchy = "payment_date"
    actions = ["mark_as_completed", "mark_as_refunded"]

    fieldsets = (
        (None, {"fields": ("booking", "amount", "payment_method")}),
        (
            _("Estado y detalles"),
            {"fields": ("status", "transaction_id", "payment_date")},
        ),
        (
            _("Información adicional"),
            {"fields": ("notes",), "classes": ("collapse",)},
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
            .select_related("booking", "booking__guest")  # noqa
        )
