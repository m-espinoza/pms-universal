from datetime import date, timedelta

from beds.models import Bed, Room
from bookings.models import Booking
from django.core.exceptions import ValidationError
from django.test import TestCase
from guests.models import Guest


class BookingModelTest(TestCase):
    def setUp(self):
        # Configuración común para las pruebas
        self.room = Room.objects.create(name="Room 101", room_type="PRIVATE")
        self.bed = Bed.objects.create(
            number=1, bed_type="SINGLE", room=self.room
        )
        self.guest = Guest.objects.create(
            name="John Doe", document_type="DNI", document_number="12345678"
        )
        self.booking = Booking.objects.create(
            guest=self.guest,
            bed=self.bed,
            check_in_date=date.today(),
            check_out_date=date.today() + timedelta(days=3),
            status="PENDING",
        )

    def test_create_booking(self):
        self.assertEqual(self.booking.guest.name, "John Doe")
        self.assertEqual(self.booking.bed.room.name, "Room 101")

    def test_booking_dates_validation(self):
        with self.assertRaises(ValidationError):
            booking = Booking(
                guest=self.guest,
                bed=self.bed,
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
            f"{self.guest} - {self.bed} "
            f"({self.booking.check_in_date} to {self.booking.check_out_date})"
        )
        self.assertEqual(str(self.booking), expected_str)

    def test_booking_total_price_calculation(self):
        # Verificar el cálculo del precio total
        nights = (
            self.booking.check_out_date - self.booking.check_in_date
        ).days
        expected_price = self.bed.base_price * nights
        self.assertEqual(self.booking.total_price, expected_price)
