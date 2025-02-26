from django.test import TestCase
from beds.models import Room, Bed
from django.core.exceptions import ValidationError

class RoomModelTest(TestCase):
    def test_create_room(self):
        # Crear una habitación
        room = Room.objects.create(
            name="Room 101",
            room_type="PRIVATE",
            capacity=2,
            description="A nice private room."
        )
        self.assertEqual(room.name, "Room 101")
        self.assertEqual(room.get_room_type_display(), "Private Room")

    def test_room_name_unique(self):
        # Verificar que el nombre de la habitación sea único
        Room.objects.create(name="Room 101", room_type="PRIVATE")
        with self.assertRaises(ValidationError):
            room = Room(name="Room 101", room_type="PRIVATE")
            room.full_clean()  # Forza la validación

class BedModelTest(TestCase):
    def test_create_bed(self):
        # Crear una habitación y una cama
        room = Room.objects.create(name="Room 101", room_type="PRIVATE")
        bed = Bed.objects.create(number=1, bed_type="SINGLE", room=room)
        self.assertEqual(bed.number, 1)
        self.assertEqual(bed.room.name, "Room 101")

    def test_bed_number_unique_per_room(self):
        # Verificar que el número de cama sea único por habitación
        room = Room.objects.create(name="Room 101", room_type="PRIVATE")
        Bed.objects.create(number=1, bed_type="SINGLE", room=room)
        with self.assertRaises(ValidationError):
            bed = Bed(number=1, bed_type="SINGLE", room=room)
            bed.full_clean()