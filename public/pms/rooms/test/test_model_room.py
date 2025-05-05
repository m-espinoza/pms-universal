from django.core.exceptions import ValidationError
from django.test import TestCase

from rooms.models import Room, Property


class RoomModelTest(TestCase):
    def setUp(self):
        # Crear primero una propiedad
        self.property = Property.objects.create(
            name="Hotel Ejemplo",
            property_type="HOTEL",
            description="Un hotel para pruebas",
        )

        # Configuración común para las pruebas
        self.room = Room.objects.create(
            property=self.property,
            name="Room 101",
            room_type="PRIVATE_ROOM",
            capacity=2,
            description="A nice private room.",
        )

    def test_create_room(self):
        self.assertEqual(self.room.name, "Room 101")
        self.assertEqual(
            self.room.get_room_type_display(), "Habitación privada"
        )  # noqa
        self.assertEqual(self.room.property.name, "Hotel Ejemplo")

    def test_room_name_unique_per_property(self):
        # El mismo nombre no debería ser válido en la misma propiedad
        with self.assertRaises(ValidationError):
            room = Room(
                property=self.property,
                name="Room 101",
                room_type="PRIVATE_ROOM",  # noqa
            )
            room.full_clean()

        # Pero el mismo nombre debería ser válido en una propiedad diferente
        another_property = Property.objects.create(
            name="Hostal Ejemplo", property_type="HOSTEL"
        )
        room = Room(
            property=another_property,
            name="Room 101",  # Mismo nombre, diferente propiedad
            room_type="PRIVATE_ROOM",
        )
        try:
            room.full_clean()
            room.save()
            self.assertTrue(True)
        except ValidationError:
            self.fail(
                "No debería lanzar ValidationError para mismo nombre en diferente propiedad"  # noqa
            )

    def test_modify_room(self):
        # Modificar la habitación
        self.room.name = "Room 102"
        self.room.save()
        updated_room = Room.objects.get(id=self.room.id)
        self.assertEqual(updated_room.name, "Room 102")

    def test_delete_room(self):
        # Eliminar la habitación
        room_id = self.room.id
        self.room.delete()
        with self.assertRaises(Room.DoesNotExist):
            Room.objects.get(id=room_id)

        # Verificar que la propiedad sigue existiendo
        self.assertTrue(Property.objects.filter(id=self.property.id).exists())

    def test_room_str_method(self):
        # Verificar el método __str__
        self.assertEqual(
            str(self.room), "Habitación Room 101 (Habitación privada)"
        )  # noqa

    def test_room_requires_property(self):
        # Una habitación debe tener una propiedad asociada
        with self.assertRaises(ValidationError):
            room = Room(name="Room sin propiedad", room_type="PRIVATE_ROOM")
            room.full_clean()

    def test_room_property_relationship(self):
        # Verificar que la relación con la propiedad funciona correctamente
        self.assertEqual(self.room.property.id, self.property.id)

        # Verificar que podemos acceder a la habitación desde la propiedad
        property_rooms = self.property.rooms.all()
        self.assertEqual(property_rooms.count(), 1)
        self.assertEqual(property_rooms.first().id, self.room.id)
