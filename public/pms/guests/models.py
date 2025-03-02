from datetime import date

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class Guest(models.Model):
    DOCUMENT_TYPES = [
        ("DNI", _("Documento Nacional de Identidad")),
        ("PASSPORT", _("Pasaporte")),
    ]

    name = models.CharField(max_length=100, verbose_name=_("Nombre"))

    document_type = models.CharField(
        max_length=8, choices=DOCUMENT_TYPES, verbose_name=_("Tipo de documento")
    )

    document_number = models.CharField(
        max_length=20, verbose_name=_("Número de documento")
    )  # noqa

    birth_date = models.DateField(
        null=True, blank=True, verbose_name=_("Fecha de nacimiento")
    )  # noqa

    phone_number = models.CharField(
        max_length=20, verbose_name=_("Número de teléfono")
    )  # noqa

    nationality = models.CharField(max_length=50, verbose_name=_("Nacionalidad"))  # noqa

    email = models.EmailField(
        max_length=254, null=True, blank=True, verbose_name=_("Correo electrónico")
    )

    reservation_owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Propietario de la reserva"),
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Huésped")
        verbose_name_plural = _("Huéspedes")

    def __str__(self):
        return self.name

    def age(self):
        if self.birth_date:
            today = date.today()
            return (
                today.year
                - self.birth_date.year
                - (
                    (today.month, today.day)
                    < (self.birth_date.month, self.birth_date.day)
                )
            )
        return None
