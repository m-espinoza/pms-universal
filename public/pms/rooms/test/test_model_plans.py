import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from rooms.models import Plan, Room, Unit


class PlanModelTest(TestCase):
    def setUp(self):
        # Create room for the plan
        self.room = Room.objects.create(
            name="Room 101",
            room_type="PRIVATE_ROOM",
            capacity=2,
            base_price=100.00,
        )

        # create unit in room for the plan
        self.unit = Unit.objects.create(
            room=self.room,
            name="Unit 101",
        )

        # Common setup for tests
        self.plan = Plan.objects.create(
            name="Plan 101",
            room=self.room,
            price=400.00,
            start_date=datetime.date(2025, 1, 1),
            end_date=datetime.date(2025, 1, 31),
            description="A nice plan.",
        )

    def test_create_plan(self):
        self.assertEqual(self.plan.name, "Plan 101")
        self.assertEqual(self.plan.price, 400.00)
        self.assertEqual(self.plan.start_date, datetime.date(2025, 1, 1))
        self.assertEqual(self.plan.end_date, datetime.date(2025, 1, 31))

    def test_plan_name_unique(self):
        with self.assertRaises(ValidationError):
            plan = Plan(name="Plan 101", room=self.room, price=400.00)
            plan.full_clean()

    def test_modify_plan(self):
        # Modificar el plan
        self.plan.name = "Plan 102"
        self.plan.save()
        updated_plan = Plan.objects.get(id=self.plan.id)
        self.assertEqual(updated_plan.name, "Plan 102")

    def test_delete_plan(self):
        # Eliminar el plan
        plan_id = self.plan.id
        self.plan.delete()
        with self.assertRaises(Plan.DoesNotExist):
            Plan.objects.get(id=plan_id)

    def test_plan_str_method(self):
        # Verificar el método __str__
        self.assertEqual(str(self.plan), "Plan Plan 101 ($400.00)")  # noqa

    def test_get_price_room(self):
        # Test get_price_room method
        price = Plan.get_price_room(
            self.unit, datetime.date(2025, 1, 1), datetime.date(2025, 1, 31)
        )
        self.assertEqual(price, 400.00)
        price = Plan.get_price_room(
            self.unit, datetime.date(2025, 2, 1), datetime.date(2025, 2, 28)
        )
        self.assertEqual(price, 100.00)
        price = Plan.get_price_room(
            self.unit, datetime.date(2025, 1, 15), datetime.date(2025, 1, 20)
        )
        self.assertEqual(price, 400.00)
        price = Plan.get_price_room(
            self.unit, datetime.date(2025, 2, 15), datetime.date(2025, 2, 20)
        )
        self.assertEqual(price, 100.00)
        price = Plan.get_price_room(
            self.unit, datetime.date(2025, 1, 1), datetime.date(2025, 2, 28)
        )
        self.assertEqual(price, 400.00)
        price = Plan.get_price_room(
            self.unit, datetime.date(2025, 2, 1), datetime.date(2025, 3, 31)
        )
        self.assertEqual(price, 100.00)
