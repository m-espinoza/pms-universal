from django.contrib import admin

from .models import Plan, Room, Unit


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "room_type",
        "base_price",
        "capacity",
        "is_active",
        "created_at",
    )
    list_filter = ("room_type", "is_active")
    search_fields = ("name", "description")
    date_hierarchy = "created_at"
    ordering = ("name",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "room_type",
                    "capacity",
                    "base_price",
                    "description",
                    "is_active",
                )
            },
        ),
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("name", "unit_type", "room", "is_active", "created_at")
    list_filter = ("unit_type", "room", "is_active")
    search_fields = ("name", "room__name")
    date_hierarchy = "created_at"
    ordering = ("room", "name")
    fieldsets = (
        (None, {"fields": ("name", "unit_type", "room", "is_active")}),  # noqa
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "room",
        "start_date",
        "end_date",
        "price",
        "is_active",
        "created_at",
    )  # noqa
    list_filter = ("room", "is_active")
    search_fields = ("name", "room__name")
    date_hierarchy = "created_at"
    ordering = ("room", "name")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "room",
                    "start_date",
                    "end_date",
                    "description",
                    "price",
                    "is_active",
                )
            },
        ),  # noqa
    )
    readonly_fields = ("created_at", "updated_at")
