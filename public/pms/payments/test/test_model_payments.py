import datetime
from decimal import Decimal

from beds.models import Bed, Room
from bookings.models import Booking
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from guests.models import Guest
from payments.models import Payment


class PaymentModelTest(TestCase):
    """Pruebas para el modelo Payment."""

    def setUp(self):
        # Crear datos de prueba
        self.room = Room.objects.create(
            name="Habitación 101",
            room_type="DORM",
            capacity=4,
            description="Habitación compartida con 4 camas",
            is_active=True,
        )

        self.bed = Bed.objects.create(
            number=1,
            bed_type="SINGLE",
            room=self.room,
            base_price=20.00,
            is_active=True,
        )

        self.guest = Guest.objects.create(
            name="Juan Pérez",
            document_type="DNI",
            document_number="12345678X",
            birth_date=datetime.date(1990, 1, 1),
            phone_number="+34666777888",
            nationality="ES",
            email="juan.perez@example.com",
        )

        # Crear una reserva para 3 días
        self.booking = Booking.objects.create(
            guest=self.guest,
            bed=self.bed,
            check_in_date=timezone.now().date() + datetime.timedelta(days=1),
            check_out_date=timezone.now().date() + datetime.timedelta(days=4),
            status="CONFIRMED",
            total_price=60.00,  # 3 noches a 20€
        )

    def test_create_payment(self):
        """Verificar que se puede crear un pago correctamente."""
        payment = Payment.objects.create(
            booking=self.booking,
            amount=Decimal("30.00"),
            payment_method="CREDIT_CARD",
            status="COMPLETED",
            transaction_id="TX123456",
        )

        self.assertEqual(payment.booking, self.booking)
        self.assertEqual(payment.amount, Decimal("30.00"))
        self.assertEqual(payment.payment_method, "CREDIT_CARD")
        self.assertEqual(payment.status, "COMPLETED")
        self.assertEqual(payment.transaction_id, "TX123456")

    def test_payment_amount_validation(self):
        """Verificar que no se pueden crear pagos con montos negativos o cero."""  # noqa
        with self.assertRaises(ValidationError):
            payment = Payment(
                booking=self.booking,
                amount=Decimal("-10.00"),
                payment_method="CASH",  # noqa
            )
            payment.full_clean()

        with self.assertRaises(ValidationError):
            payment = Payment(
                booking=self.booking,
                amount=Decimal("0.00"),
                payment_method="CASH",  # noqa
            )
            payment.full_clean()

    def test_mark_as_completed(self):
        """Verificar que el método mark_as_completed funciona correctamente."""
        # Cambiar la reserva a pendiente de pago
        self.booking.status = "PENDING_PAYMENT"
        self.booking.save()

        # Crear un pago por el monto total
        payment = Payment.objects.create(
            booking=self.booking,
            amount=Decimal("60.00"),
            payment_method="CREDIT_CARD",
            status="PENDING",
        )

        # Marcar el pago como completado
        payment.mark_as_completed()

        # Refrescar la reserva desde la base de datos
        self.booking.refresh_from_db()

        # Verificar que el pago está completado
        self.assertEqual(payment.status, "COMPLETED")

        # Verificar que la reserva está confirmada
        self.assertEqual(self.booking.status, "CONFIRMED")

    def test_partial_payment(self):
        """Verificar que se pueden hacer pagos parciales."""
        # Cambiar la reserva a pendiente de pago
        self.booking.status = "PENDING_PAYMENT"
        self.booking.save()

        # Primer pago (parcial)
        payment1 = Payment.objects.create(
            booking=self.booking,
            amount=Decimal("30.00"),  # 50% del total
            payment_method="CASH",
            status="PENDING",
        )

        payment1.mark_as_completed()

        # Refrescar la reserva desde la base de datos
        self.booking.refresh_from_db()

        # La reserva debería seguir pendiente porque el pago fue parcial
        self.assertEqual(self.booking.status, "PENDING_PAYMENT")

        # Segundo pago (resto)
        payment2 = Payment.objects.create(
            booking=self.booking,
            amount=Decimal("30.00"),  # Otro 50%
            payment_method="CREDIT_CARD",
            status="PENDING",
        )

        payment2.mark_as_completed()

        # Refrescar la reserva desde la base de datos
        self.booking.refresh_from_db()

        # Ahora la reserva debería estar confirmada
        self.assertEqual(self.booking.status, "CONFIRMED")

    def test_refund(self):
        """Verificar que el método refund funciona correctamente."""
        payment = Payment.objects.create(
            booking=self.booking,
            amount=Decimal("60.00"),
            payment_method="CREDIT_CARD",
            status="COMPLETED",
        )

        # Reembolso parcial
        payment.refund(Decimal("20.00"))
        self.assertEqual(payment.status, "PARTIALLY_REFUNDED")

        # Crear un nuevo pago para probar el reembolso completo
        payment2 = Payment.objects.create(
            booking=self.booking,
            amount=Decimal("30.00"),
            payment_method="CASH",
            status="COMPLETED",
        )

        # Reembolso completo
        payment2.refund()
        self.assertEqual(payment2.status, "REFUNDED")

        # Verificar que no se puede reembolsar más del monto del pago
        payment3 = Payment.objects.create(
            booking=self.booking,
            amount=Decimal("20.00"),
            payment_method="PAYPAL",
            status="COMPLETED",
        )

        with self.assertRaises(ValueError):
            payment3.refund(Decimal("30.00"))
