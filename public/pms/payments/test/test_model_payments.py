import datetime
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User

from beds.models import Bed, Room
from bookings.models import Booking
from guests.models import Guest
from payments.models import Payment, CashRegisterEntry


class PaymentModelTest(TestCase):
    """Pruebas simplificadas para el modelo Payment."""

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
            status="PENDING",  # Usando valores cortos por si hay limitación
            total_price=60.00,  # 3 noches a 20€
        )

        # Crear un usuario para el campo created_by
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )

    def test_create_payment(self):
        """Verificar que se puede crear un pago correctamente."""
        payment = Payment.objects.create(
            booking=self.booking,
            amount=Decimal("30.00"),
            payment_method="CREDIT_CARD",
            status="COMPLETED",
            transaction_id="TX123456",
            created_by=self.user,  # Añadir created_by
        )

        self.assertEqual(payment.booking, self.booking)
        self.assertEqual(payment.amount, Decimal("30.00"))
        self.assertEqual(payment.payment_method, "CREDIT_CARD")
        self.assertEqual(payment.status, "COMPLETED")
        self.assertEqual(payment.transaction_id, "TX123456")
        self.assertEqual(payment.created_by, self.user)  # Verificar created_by

    def test_payment_status_no_payment(self):
        """Verificar el estado de pago cuando no hay pagos."""
        # No creamos ningún pago
        self.assertEqual(self.booking.get_payment_status(), "NO_PAYMENT")

    def test_payment_status_partial_payment(self):
        """Verificar el estado de pago cuando hay pagos parciales."""
        # Creamos un pago parcial (50%)
        Payment.objects.create(
            booking=self.booking,
            amount=Decimal("30.00"),
            payment_method="CASH",
            status="COMPLETED",
            created_by=self.user,  # Añadir created_by
        )

        self.assertEqual(self.booking.get_payment_status(), "PARTIAL_PAYMENT")

    def test_payment_status_fully_paid(self):
        """Verificar el estado de pago cuando está completamente pagado."""
        # Creamos un pago por el monto total
        Payment.objects.create(
            booking=self.booking,
            amount=Decimal("60.00"),
            payment_method="CREDIT_CARD",
            status="COMPLETED",
            created_by=self.user,  # Añadir created_by
        )

        self.assertEqual(self.booking.get_payment_status(), "FULLY_PAID")

    def test_multiple_payments_to_complete(self):
        """Verificar que múltiples pagos pueden completar el pago total."""
        # Primer pago (50%)
        Payment.objects.create(
            booking=self.booking,
            amount=Decimal("30.00"),
            payment_method="CASH",
            status="COMPLETED",
            created_by=self.user,  # Añadir created_by
        )

        self.assertEqual(self.booking.get_payment_status(), "PARTIAL_PAYMENT")

        # Segundo pago (50% restante)
        Payment.objects.create(
            booking=self.booking,
            amount=Decimal("30.00"),
            payment_method="CREDIT_CARD",
            status="COMPLETED",
            created_by=self.user,  # Añadir created_by
        )

        self.assertEqual(self.booking.get_payment_status(), "FULLY_PAID")

    def test_pending_payments_not_counted(self):
        """Verificar que los pagos pendientes no se cuentan en el estado de pago."""
        # Creamos un pago pendiente
        payment = Payment.objects.create(
            booking=self.booking,
            amount=Decimal("60.00"),
            payment_method="BANK_TRANSFER",
            status="PENDING",  # Pago pendiente
            created_by=self.user,  # Añadir created_by
        )

        # El estado debería seguir siendo NO_PAYMENT
        # ya que el pago está pendiente
        self.assertEqual(self.booking.get_payment_status(), "NO_PAYMENT")

        # Ahora marcamos el pago como completado
        payment.status = "COMPLETED"
        payment.save()

        # Ahora el estado debería ser FULLY_PAID
        self.assertEqual(self.booking.get_payment_status(), "FULLY_PAID")

    def test_payment_exceeding_debt(self):
        """Verificar que no se pueden crear pagos que excedan la deuda pendiente."""
        # Crear un pago parcial
        Payment.objects.create(
            booking=self.booking,
            amount=Decimal("40.00"),
            payment_method="CASH",
            status="COMPLETED",
            created_by=self.user,  # Añadir created_by
        )

        # Verificar que el estado de pago es parcial
        self.assertEqual(self.booking.get_payment_status(), "PARTIAL_PAYMENT")

        # Intentar crear un pago que excede la deuda pendiente (20.00)
        with self.assertRaises(ValidationError) as context:
            Payment.objects.create(
                booking=self.booking,
                amount=Decimal("30.00"),  # Excede en 10.00
                payment_method="CREDIT_CARD",
                status="COMPLETED",
                created_by=self.user,  # Añadir created_by
            )

        # Verificar que el mensaje de error contiene la información del exceso
        self.assertIn("excede la deuda pendiente por", str(context.exception))

        # Crear un pago por el monto exacto de la deuda pendiente
        Payment.objects.create(
            booking=self.booking,
            amount=Decimal("20.00"),
            payment_method="CREDIT_CARD",
            status="COMPLETED",
            created_by=self.user,  # Añadir created_by
        )

        # Verificar que ahora el estado es totalmente pagado
        self.assertEqual(self.booking.get_payment_status(), "FULLY_PAID")

    def test_negative_payment_amount(self):
        """Verificar que no se pueden crear pagos con montos negativos."""
        with self.assertRaises(ValidationError):
            payment = Payment(
                booking=self.booking,
                amount=Decimal("-10.00"),
                payment_method="CASH",
                status="PENDING",
                created_by=self.user,  # Añadir created_by
            )
            payment.full_clean()

    def test_zero_payment_amount(self):
        """Verificar que no se pueden crear pagos con monto cero."""
        with self.assertRaises(ValidationError):
            payment = Payment(
                booking=self.booking,
                amount=Decimal("0.00"),
                payment_method="CREDIT_CARD",
                status="PENDING",
                created_by=self.user,  # Añadir created_by
            )
            payment.full_clean()

    def test_very_small_payment_amount(self):
        """Verificar que no se pueden crear pagos con montos extremadamente pequeños."""
        with self.assertRaises(ValidationError):
            payment = Payment(
                booking=self.booking,
                amount=Decimal("0.001"),  # Menos de un céntimo
                payment_method="BANK_TRANSFER",
                status="PENDING",
                created_by=self.user,  # Añadir created_by
            )
            payment.full_clean()

    def test_saving_invalid_payment_fails(self):
        """Verificar que el guardado de un pago inválido falla a nivel de base de datos."""
        # Intentamos crear directamente un pago con monto cero
        # Nota: Esto intentará saltarse las validaciones del modelo,
        # pero debería fallar a nivel de base de datos
        # si los validadores de campo están configurados correctamente
        with self.assertRaises(Exception):
            Payment.objects.create(
                booking=self.booking,
                amount=Decimal("0.00"),
                payment_method="PAYPAL",
                status="PENDING",
                created_by=self.user,  # Añadir created_by
            )

    def test_cash_register_entry_creation(self):
        """Verificar que se crea una entrada en la caja
        cuando se marca un pago en efectivo como completado."""
        payment = Payment.objects.create(
            booking=self.booking,
            amount=Decimal("30.00"),
            payment_method="CASH",
            status="COMPLETED",
            created_by=self.user,  # Añadir created_by
        )

        # Verificar que se creó una entrada en la caja
        entry = CashRegisterEntry.objects.filter(payment=payment).first()
        self.assertIsNotNone(entry)
        self.assertEqual(entry.entry_type, "DEPOSIT")
        self.assertEqual(entry.amount, Decimal("30.00"))
        self.assertEqual(entry.description, f"Pago en efectivo de reserva #{self.booking.id}")

    def test_cash_register_entry_on_refund(self):
        """Verificar que se crea una entrada en la caja
        cuando se realiza un reembolso en efectivo."""
        payment = Payment.objects.create(
            booking=self.booking,
            amount=Decimal("30.00"),
            payment_method="CASH",
            status="COMPLETED",
            created_by=self.user,
        )

        # Realizar un reembolso parcial
        payment.refund(amount=Decimal("10.00"), user=self.user)

        # Verificar que se creó una entrada en la caja para el reembolso
        entry = CashRegisterEntry.objects.filter(payment=payment, entry_type="WITHDRAWAL").first()
        self.assertIsNotNone(entry)
        self.assertEqual(entry.amount, Decimal("10.00"))
        self.assertEqual(entry.description, f"Reembolso en efectivo de reserva #{self.booking.id}")