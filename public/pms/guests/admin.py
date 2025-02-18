from django.contrib import admin
from .models import Guest

@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'email', 'nationality', 'created_at')
    list_filter = ('name', 'nationality')
    search_fields = ('name', 'phone_number', 'email', 'nationality')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    fieldsets = (
        (None, {
            'fields': ('name', 'phone_number ', 'email', 'nationality')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')