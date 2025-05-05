import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from rooms.models import Plan, Room, Unit, Property


class PlanModelTest(TestCase):
    def setUp(self):
        # Crear primero una propiedad
        self.property = Property.objects.create(
            name="Resort Example",
            property_type="RESORT",
            description="A test resort",  # noqa
        )

        # Create room for the plan, associated with the property
        self.room = Room.objects.create(
            property=self.property,
            name="Room 101",
            room_type="PRIVATE_ROOM",
            capacity=2,
            base_price=100.00,
        )

        # create unit in room for the plan
        self.unit = Unit.objects.create(
            room=self.room, name="Unit 101", unit_type="QUEEN_BED"
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
        # Verificar la relación con room y property
        self.assertEqual(self.plan.room.name, "Room 101")
        self.assertEqual(self.plan.room.property.name, "Resort Example")

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

        # Verificar que la habitación, unidad y propiedad siguen existiendo
        self.assertTrue(Room.objects.filter(id=self.room.id).exists())
        self.assertTrue(Unit.objects.filter(id=self.unit.id).exists())
        self.assertTrue(Property.objects.filter(id=self.property.id).exists())

    def test_plan_str_method(self):
        # Verificar el método __str__
        self.assertEqual(str(self.plan), "Plan Plan 101 ($400.00)")

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

    def test_multiple_properties_and_plans(self):
        # Crear una segunda propiedad
        property2 = Property.objects.create(
            name="Hostel Example", property_type="HOSTEL"
        )

        # Crear una habitación en la segunda propiedad
        room2 = Room.objects.create(
            property=property2,
            name="Room 101",  # Mismo nombre pero diferente propiedad
            room_type="DORM",
            capacity=8,
            base_price=50.00,
        )

        # Crear un plan para la segunda habitación
        plan2 = Plan.objects.create(
            name="Plan Economy",  # Nombre diferente al primer plan
            room=room2,
            price=200.00,
            start_date=datetime.date(2025, 1, 1),
            end_date=datetime.date(2025, 1, 31),
        )

        # Verificar que ambos planes existen y tienen relaciones correctas
        self.assertEqual(Plan.objects.count(), 2)
        self.assertEqual(plan2.room.property.name, "Hostel Example")

        # Verificar que los planes funcionan independientemente
        # para diferentes propiedades
        unit2 = Unit.objects.create(
            room=room2, name="Bed 1", unit_type="BUNK_BED"
        )  # noqa

        price_property1 = Plan.get_price_room(
            self.unit, datetime.date(2025, 1, 15), datetime.date(2025, 1, 20)
        )
        price_property2 = Plan.get_price_room(
            unit2, datetime.date(2025, 1, 15), datetime.date(2025, 1, 20)
        )

        self.assertEqual(price_property1, 400.00)
        self.assertEqual(price_property2, 200.00)
