from django.test import TestCase
from beds.models import Room, Bed
from django.core.exceptions import ValidationError


class BedModelTest(TestCase):
    def setUp(self):
        # Configuración común para las pruebas
        self.room = Room.objects.create(name="Room 101", room_type="PRIVATE")
        self.bed = Bed.objects.create(
            number=1,
            bed_type="SINGLE",
            room=self.room
        )

    def test_create_bed(self):
        self.assertEqual(self.bed.number, 1)
        self.assertEqual(self.bed.room.name, "Room 101")

    def test_bed_number_unique_per_room(self):
        with self.assertRaises(ValidationError):
            bed = Bed(number=1, bed_type="SINGLE", room=self.room)
            bed.full_clean()

    def test_modify_bed(self):
        # Modificar la cama
        self.bed.number = 2
        self.bed.save()
        updated_bed = Bed.objects.get(id=self.bed.id)
        self.assertEqual(updated_bed.number, 2)

    def test_delete_bed(self):
        # Eliminar la cama
        bed_id = self.bed.id
        self.bed.delete()
        with self.assertRaises(Bed.DoesNotExist):
            Bed.objects.get(id=bed_id)
            