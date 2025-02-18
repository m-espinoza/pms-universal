from django.contrib import admin
from .models import Room, Bed

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'room_type', 'capacity', 'is_active', 'created_at')
    list_filter = ('room_type', 'is_active')
    search_fields = ('name', 'description')
    date_hierarchy = 'created_at'
    ordering = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', 'room_type', 'capacity', 'description', 'is_active')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ('number', 'bed_type', 'room', 'base_price', 'is_active', 'created_at')
    list_filter = ('bed_type', 'room', 'is_active')
    search_fields = ('number', 'room__name')
    date_hierarchy = 'created_at'
    ordering = ('room', 'number')
    fieldsets = (
        (None, {
            'fields': ('number', 'bed_type', 'room', 'base_price', 'is_active')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')