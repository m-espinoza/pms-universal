from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "guest",
        "unit",
        "check_in_date",
        "check_out_date",
        "status",
        "total_price",
    )
    list_filter = ("status", "unit", "check_in_date", "check_out_date")
    search_fields = ("guest__name", "unit__name", "notes")
    date_hierarchy = "check_in_date"
    ordering = ("-created_at",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "guest",
                    "unit",
                    "check_in_date",
                    "check_out_date",
                    "status",
                    "total_price",
                    "notes",
                )
            },
        ),
    )
    readonly_fields = ("created_at", "updated_at")
