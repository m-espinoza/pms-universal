from django.contrib import admin

from .models import Plan, Room, Unit, Property


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "property_type",
        "is_active",
        "created_at",
    )
    list_filter = ("property_type", "is_active")
    search_fields = ("name", "description", "address")
    date_hierarchy = "created_at"
    ordering = ("name",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "property_type",
                    "description",
                    "address",
                    "is_active",
                )
            },
        ),
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "property",  # Añadido property
        "room_type",
        "base_price",
        "capacity",
        "is_active",
        "created_at",
    )
    list_filter = ("property", "room_type", "is_active")  # Añadido property al filtro
    search_fields = ("name", "description", "property__name")  # Añadido búsqueda por property
    date_hierarchy = "created_at"
    ordering = ("property", "name")  # Ordenar primero por property
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "property",  # Añadido property en el formulario
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
    list_filter = ("unit_type", "room__property", "room", "is_active")  # Filtro por property de la room
    search_fields = ("name", "room__name", "room__property__name")  # Búsqueda por property
    date_hierarchy = "created_at"
    ordering = ("room__property", "room", "name")  # Ordenar primero por property de la room
    fieldsets = (
        (None, {"fields": ("name", "unit_type", "room", "is_active")}),  # noqa
    )
    readonly_fields = ("created_at", "updated_at")
    
    # Filtro jerárquico que muestra primero las propiedades y luego las habitaciones de la propiedad seleccionada
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "room":
            kwargs["queryset"] = Room.objects.select_related("property").all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


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
    list_filter = ("room__property", "room", "is_active")  # Filtrar por property de la room
    search_fields = ("name", "room__name", "room__property__name")  # Búsqueda por property
    date_hierarchy = "created_at"
    ordering = ("room__property", "room", "name")  # Ordenar primero por property de la room
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
    
    # Filtro jerárquico que muestra primero las propiedades y luego las habitaciones de la propiedad seleccionada
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "room":
            kwargs["queryset"] = Room.objects.select_related("property").all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)