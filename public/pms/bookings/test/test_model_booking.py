from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase

from bookings.models import Booking
from guests.models import Guest
from rooms.models import Property, Room, Unit


class BookingModelTest(TestCase):
    def setUp(self):
        # Configuración común para las pruebas
        # Crear primero una propiedad
        self.property = Property.objects.create(
            name="Hotel Example",
            property_type="HOTEL",
            description="A test hotel"
        )
        self.room = Room.objects.create(
            property=self.property,
            name="Room 101",
            room_type="PRIVATE",
            base_price=100
        )
        self.unit = Unit.objects.create(
            name="1", unit_type="SINGLE", room=self.room
        )  # noqa
        self.guest = Guest.objects.create(
            name="John Doe", document_type="DNI", document_number="12345678"
        )
        self.booking = Booking.objects.create(
            guest=self.guest,
            unit=self.unit,
            check_in_date=date.today(),
            check_out_date=date.today() + timedelta(days=3),
            total_price=self.room.base_price * 3,
            status="PENDING",
        )

    def test_create_booking(self):
        self.assertEqual(self.booking.guest.name, "John Doe")
        self.assertEqual(self.booking.unit.room.name, "Room 101")

    def test_booking_dates_validation(self):
        with self.assertRaises(ValidationError):
            booking = Booking(
                guest=self.guest,
                unit=self.unit,
                check_in_date=date.today(),
                check_out_date=date.today() - timedelta(days=1),
            )
            booking.full_clean()

    def test_modify_booking(self):
        # Modificar la reserva
        self.booking.status = "CONFIRMED"
        self.booking.save()
        updated_booking = Booking.objects.get(id=self.booking.id)
        self.assertEqual(updated_booking.status, "CONFIRMED")

    def test_delete_booking(self):
        # Eliminar la reserva
        booking_id = self.booking.id
        self.booking.delete()
        with self.assertRaises(Booking.DoesNotExist):
            Booking.objects.get(id=booking_id)

    def test_booking_str_method(self):
        # Verificar el método __str__
        expected_str = (
            f"{self.guest} - {self.unit} "
            f"({self.booking.check_in_date} to {self.booking.check_out_date})"
        )
        self.assertEqual(str(self.booking), expected_str)

    def test_booking_total_price_calculation(self):
        # Verificar el cálculo del precio total
        nights = (self.booking.check_out_date - self.booking.check_in_date).days  # noqa
        expected_price = self.room.base_price * nights
        self.assertEqual(self.booking.total_price, expected_price)
