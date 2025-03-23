from rooms.models import Unit, Room
from django.core.exceptions import ValidationError
from django.test import TestCase


class UnitModelTest(TestCase):
    def setUp(self):
        # Configuración común para las pruebas
        self.room = Room.objects.create(name="Room 101", room_type="PRIVATE")
        self.unit = Unit.objects.create(
            name="1", unit_type="SINGLE", room=self.room
        )  # noqa

    def test_create_unit(self):
        self.assertEqual(self.unit.name, "1")
        self.assertEqual(self.unit.room.name, "Room 101")

    def test_unit_number_unique_per_room(self):
        with self.assertRaises(ValidationError):
            unit = Unit(name="1", unit_type="SINGLE", room=self.room)
            unit.full_clean()

    def test_modify_unit(self):
        # Modificar la unidad
        self.unit.name = "2"
        self.unit.save()
        updated_unit = Unit.objects.get(id=self.unit.id)
        self.assertEqual(updated_unit.name, "2")

    def test_delete_unit(self):
        # Eliminar la unidad
        unit_id = self.unit.id
        self.unit.delete()
        with self.assertRaises(Unit.DoesNotExist):
            Unit.objects.get(id=unit_id)
