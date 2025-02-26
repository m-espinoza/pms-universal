from datetime import date

from django.test import TestCase
from guests.models import Guest


class GuestModelTest(TestCase):
    def setUp(self):
        # Configuración común para las pruebas
        self.guest = Guest.objects.create(
            name="John Doe",
            document_type="DNI",
            document_number="12345678",
            birth_date=date(1990, 1, 1),
            phone_number="+123456789",
            nationality="Argentinian",
        )

    def test_create_guest(self):
        self.assertEqual(self.guest.name, "John Doe")
        self.assertEqual(self.guest.age(), 35)

    def test_guest_email_optional(self):
        self.assertIsNone(self.guest.email)

    def test_modify_guest(self):
        # Modificar el huésped
        self.guest.name = "Jane Doe"
        self.guest.save()
        updated_guest = Guest.objects.get(id=self.guest.id)
        self.assertEqual(updated_guest.name, "Jane Doe")

    def test_delete_guest(self):
        # Eliminar el huésped
        guest_id = self.guest.id
        self.guest.delete()
        with self.assertRaises(Guest.DoesNotExist):
            Guest.objects.get(id=guest_id)

    def test_guest_str_method(self):
        # Verificar el método __str__
        self.assertEqual(str(self.guest), "John Doe")
