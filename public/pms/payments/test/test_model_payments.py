import datetime
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from rooms.models import Unit, Room
from bookings.models import Booking
from guests.models import Guest
from payments.models import CashRegisterEntry, Payment


class PaymentModelTest(TestCase):
    """Pruebas para el modelo Payment con soporte para reembolsos."""

    def setUp(self):
        # Crear datos de prueba
        self.room = Room.objects.create(
            name="Habitación 101",
            room_type="DORM",
            capacity=4,
            base_price=20.00,
            description="Habitación compartida con 4 camas",
            is_active=True,
        )

        self.unit = Unit.objects.create(
            name="1",
            unit_type="SINGLE",
            room=self.room,            
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
            unit=self.unit,
            check_in_date=timezone.now().date() + datetime.timedelta(days=1),
            check_out_date=timezone.now().date() + datetime.timedelta(days=4),
            status="PENDING",
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
            created_by=self.user,
        )

        self.assertEqual(payment.booking, self.booking)
        self.assertEqual(payment.amount, Decimal("30.00"))
        self.assertEqual(payment.payment_method, "CREDIT_CARD")
        self.assertEqual(payment.status, "COMPLETED")
        self.assertEqual(payment.transaction_id, "TX123456")
        self.assertEqual(payment.created_by, self.user)
        self.assertEqual(payment.payment_type, "PAYMENT")

    def test_payment_status_fully_paid(self):
        """Verificar el estado de pago cuando está completamente pagado."""
        # Creamos un pago por el monto total
        Payment.objects.create(
            booking=self.booking,
            amount=Decimal("60.00"),
            payment_method="CREDIT_CARD",
            status="COMPLETED",
            created_by=self.user,
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
            created_by=self.user,
        )

        self.assertEqual(self.booking.get_payment_status(), "PARTIAL_PAYMENT")

        # Segundo pago (50% restante)
        Payment.objects.create(
            booking=self.booking,
            amount=Decimal("30.00"),
            payment_method="CREDIT_CARD",
            status="COMPLETED",
            created_by=self.user,
        )

        self.assertEqual(self.booking.get_payment_status(), "FULLY_PAID")

    def test_payment_exceeding_debt(self):
        """
        Verificar que no se pueden crear pagos que excedan la deuda pendiente.
        """
        # Crear un pago parcial
        Payment.objects.create(
            booking=self.booking,
            amount=Decimal("40.00"),
            payment_method="CASH",
            status="COMPLETED",
            created_by=self.user,
        )

        # Intentar crear un pago que excede la deuda pendiente (20.00)
        with self.assertRaises(ValidationError) as context:
            Payment.objects.create(
                booking=self.booking,
                amount=Decimal("30.00"),
                payment_method="CREDIT_CARD",
                status="COMPLETED",
                created_by=self.user,
            )

        # Verificar que el mensaje de error contiene la información del exceso
        self.assertIn("excede la deuda pendiente por", str(context.exception))

    def test_negative_payment_amount(self):
        """Verificar que no se pueden crear pagos con montos negativos."""
        with self.assertRaises(ValidationError):
            payment = Payment(
                booking=self.booking,
                amount=Decimal("-10.00"),
                payment_method="CASH",
                status="PENDING",
                created_by=self.user,
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
                created_by=self.user,
            )
            payment.full_clean()

    def test_cash_register_entry_creation(self):
        """
        Verificar que se crea una entrada en la caja
        cuando se marca un pago en efectivo como completado.
        """
        payment = Payment.objects.create(
            booking=self.booking,
            amount=Decimal("30.00"),
            payment_method="CASH",
            status="COMPLETED",
            created_by=self.user,
        )

        # Verificar que se creó una entrada en la caja
        entry = CashRegisterEntry.objects.filter(payment=payment).first()
        self.assertIsNotNone(entry)
        self.assertEqual(entry.entry_type, "DEPOSIT")
        self.assertEqual(entry.amount, Decimal("30.00"))
        self.assertEqual(
            entry.description, f"Pago en efectivo de reserva #{self.booking.id}"  # noqa
        )

    # Nuevas pruebas para reembolsos
    def test_create_refund(self):
        """
        Verificar que se puede crear un reembolso
        correctamente usando el método refund().
        """
        # Crear un pago
        payment = Payment.objects.create(
            booking=self.booking,
            amount=Decimal("30.00"),
            payment_method="CASH",
            status="COMPLETED",
            created_by=self.user,
        )

        # Crear un reembolso
        refund = payment.refund(amount=Decimal("10.00"), user=self.user)

        # Verificar que el reembolso se creó correctamente
        self.assertEqual(refund.booking, self.booking)
        self.assertEqual(refund.amount, Decimal("-10.00"))
        self.assertEqual(refund.payment_method, "CASH")
        self.assertEqual(refund.status, "COMPLETED")
        self.assertEqual(refund.payment_type, "REFUND")
        self.assertEqual(refund.original_payment, payment)
        self.assertEqual(refund.created_by, self.user)

    def test_create_refund_full_amount(self):
        """Verificar que se puede crear un reembolso por el monto total."""
        # Crear un pago
        payment = Payment.objects.create(
            booking=self.booking,
            amount=Decimal("30.00"),
            payment_method="CREDIT_CARD",
            status="COMPLETED",
            created_by=self.user,
        )

        # Crear un reembolso por el monto total
        refund = payment.refund(user=self.user)  # Sin especificar amount

        # Verificar que el reembolso se creó por el monto total
        self.assertEqual(refund.amount, Decimal("-30.00"))
        self.assertEqual(refund.payment_type, "REFUND")

    def test_refund_exceeding_original_payment(self):
        """Verificar que no se puede reembolsar más del monto original."""
        # Crear un pago
        payment = Payment.objects.create(
            booking=self.booking,
            amount=Decimal("30.00"),
            payment_method="CASH",
            status="COMPLETED",
            created_by=self.user,
        )

        # Intentar reembolsar más del monto original
        with self.assertRaises(ValueError) as context:
            payment.refund(amount=Decimal("40.00"), user=self.user)

        self.assertIn(
            "no puede ser mayor que el monto del pago", str(context.exception)
        )

    def test_refund_cash_creates_withdrawal_in_cash_register(self):
        """
        Verificar que un reembolso en efectivo
        crea una entrada de retiro en la caja.
        """
        # Crear un pago en efectivo
        payment = Payment.objects.create(
            booking=self.booking,
            amount=Decimal("30.00"),
            payment_method="CASH",
            status="COMPLETED",
            created_by=self.user,
        )

        # Realizar un reembolso
        refund = payment.refund(amount=Decimal("10.00"), user=self.user)

        # Verificar que se creó una entrada de retiro en la caja
        entry = CashRegisterEntry.objects.filter(payment=refund).first()
        self.assertIsNotNone(entry)
        self.assertEqual(entry.entry_type, "WITHDRAWAL")
        self.assertEqual(entry.amount, Decimal("10.00"))  # Valor absoluto
        self.assertIn(
            f"Reembolso en efectivo de reserva #{self.booking.id}",
            entry.description,  # noqa
        )

    def test_refund_non_cash_payment_no_cash_register_entry(self):
        """
        Verificar que un reembolso de un pago
        que no es en efectivo no crea entrada en caja.
        """
        # Crear un pago con tarjeta
        payment = Payment.objects.create(
            booking=self.booking,
            amount=Decimal("30.00"),
            payment_method="CREDIT_CARD",
            status="COMPLETED",
            created_by=self.user,
        )

        # Realizar un reembolso
        refund = payment.refund(amount=Decimal("10.00"), user=self.user)

        # Verificar que no se creó entrada en caja
        entry = CashRegisterEntry.objects.filter(payment=refund).first()
        self.assertIsNone(entry)

    def test_payment_balance_after_refunds(self):
        """
        Verificar que el balance de pagos
        se calcula correctamente después de reembolsos.
        """
        # Crear un pago completo
        Payment.objects.create(
            booking=self.booking,
            amount=Decimal("60.00"),
            payment_method="CASH",
            status="COMPLETED",
            created_by=self.user,
        )

        # Inicialmente está totalmente pagado
        self.assertEqual(self.booking.get_payment_status(), "FULLY_PAID")

        # Reembolsar la mitad
        payment = Payment.objects.first()
        payment.refund(amount=Decimal("30.00"), user=self.user)

        # Ahora debería estar parcialmente pagado
        self.assertEqual(self.booking.get_payment_status(), "PARTIAL_PAYMENT")

        # Reembolsar el resto
        payment.refund(amount=Decimal("30.00"), user=self.user)

        # Ahora no debería tener ningún pago
        self.assertEqual(self.booking.get_payment_status(), "NO_PAYMENT")

    def test_refund_with_pending_status(self):
        """Verificar que se puede crear un reembolso con estado pendiente."""
        # Crear un pago
        payment = Payment.objects.create(
            booking=self.booking,
            amount=Decimal("60.00"),
            payment_method="BANK_TRANSFER",
            status="COMPLETED",
            created_by=self.user,
        )

        # Crear manualmente un reembolso con estado pendiente
        refund = Payment.objects.create(
            booking=self.booking,
            amount=Decimal("-10.00"),
            payment_method="BANK_TRANSFER",
            status="PENDING",  # Pendiente
            payment_type="REFUND",
            original_payment=payment,
            created_by=self.user,
        )

        # Verificar que se creó correctamente
        self.assertEqual(refund.status, "PENDING")
        self.assertEqual(refund.payment_type, "REFUND")

        # Verificar que no afecta al balance de pagos hasta que esté completado
        self.assertEqual(self.booking.get_payment_status(), "FULLY_PAID")

        # Completar el reembolso
        refund.mark_as_completed(self.user)

        # Ahora sí debería afectar al balance
        self.assertEqual(self.booking.get_payment_status(), "PARTIAL_PAYMENT")


class CashRegisterEntryTest(TestCase):
    """Pruebas para el modelo CashRegisterEntry con soporte para reembolsos."""

    def setUp(self):
        # Crear datos de prueba
        self.room = Room.objects.create(
            name="Habitación 101",
            room_type="DORM",
            capacity=4,
            base_price=20.00,
            description="Habitación compartida con 4 camas",
            is_active=True,
        )

        self.unit = Unit.objects.create(
            name="1",
            unit_type="SINGLE",
            room=self.room,            
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

        self.booking = Booking.objects.create(
            guest=self.guest,
            unit=self.unit,
            check_in_date=timezone.now().date() + datetime.timedelta(days=1),
            check_out_date=timezone.now().date() + datetime.timedelta(days=4),
            status="PENDING",
            total_price=60.00,
        )

        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )

    def test_cash_register_balance_after_multiple_operations(self):
        """
        Verificar el saldo de la caja después
        de múltiples operaciones incluyendo reembolsos.
        """
        # Primer pago en efectivo
        payment1 = Payment.objects.create(
            booking=self.booking,
            amount=Decimal("30.00"),
            payment_method="CASH",
            status="COMPLETED",
            created_by=self.user,
        )

        # Segundo pago en efectivo
        Payment.objects.create(
            booking=self.booking,
            amount=Decimal("20.00"),
            payment_method="CASH",
            status="COMPLETED",
            created_by=self.user,
        )

        # Reembolso parcial del primer pago
        payment1.refund(amount=Decimal("15.00"), user=self.user)

        # Verificar el saldo de la caja
        balance = CashRegisterEntry.get_current_balance()
        self.assertEqual(balance, Decimal("35.00"))  # 30 + 20 - 15 = 35

    def test_cash_register_balance_with_non_cash_payments(self):
        """
        Verificar que los pagos y reembolsos
        que no son en efectivo no afectan la caja.
        """
        # Pago en efectivo
        Payment.objects.create(
            booking=self.booking,
            amount=Decimal("30.00"),
            payment_method="CASH",
            status="COMPLETED",
            created_by=self.user,
        )

        # Pago con tarjeta
        payment2 = Payment.objects.create(
            booking=self.booking,
            amount=Decimal("20.00"),
            payment_method="CREDIT_CARD",
            status="COMPLETED",
            created_by=self.user,
        )

        # Reembolso del pago con tarjeta
        payment2.refund(amount=Decimal("10.00"), user=self.user)

        # Verificar el saldo de la caja
        # (solo debería contar el pago en efectivo)
        balance = CashRegisterEntry.get_current_balance()
        self.assertEqual(balance, Decimal("30.00"))
