from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class Room(models.Model):
    ROOM_TYPES = [
        ('DORM', _('Dormitory')),
        ('PRIVATE', _('Private Room')),
    ]

    name = models.CharField(
        max_length=50,
        verbose_name=_('name'),
        help_text=_('Room name should be unique')
    )

    room_type = models.CharField(
        max_length=7, 
        choices=ROOM_TYPES,
        verbose_name=_('room type')
    )

    base_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0.00,
        verbose_name=_('base price')
    )

    capacity = models.IntegerField(
        verbose_name=_('capacity'),
        blank=True,
        default=1
        )
    description = models.TextField(
        blank=True,
        verbose_name=_('description'),
        help_text=_('Room description (private bathroom, amenities, etc.')
    )    

    is_active = models.BooleanField(
        default=True,
        verbose_name=_('is active')
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('room')
        verbose_name_plural = _('rooms')
        ordering = ['name']

    def __str__(self):
        return f"{_('Room')} {self.number} ({self.get_room_type_display()})"

class Bed(models.Model):
    BED_TYPES = [
        ('SINGLE', _('Single Bed')),
        ('BUNK_TOP', _('Top Bunk')),
        ('BUNK_BOTTOM', _('Bottom Bunk')),
        ('DOUBLE', _('Double Bed')),
    ]

    number = models.IntegerField(
        verbose_name=_('number'),
        null=True,
        blank=True,
    )

    bed_type = models.CharField(
        max_length=11, 
        choices=BED_TYPES,
        verbose_name=_('bed type'),
        default='SINGLE',
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='beds',
        verbose_name=_('room')
    )

    base_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0.00,
        verbose_name=_('base price')
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_('is active')
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('bed')
        verbose_name_plural = _('beds')
        unique_together = ['room', 'number']