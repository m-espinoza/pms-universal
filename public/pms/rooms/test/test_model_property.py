from django.core.exceptions import ValidationError
from django.test import TestCase

from rooms.models import Property


class PropertyModelTest(TestCase):
    def setUp(self):
        # Configuración común para las pruebas
        self.property = Property.objects.create(
            name="Hotel Los Pinos",
            property_type="HOTEL",
            description="Un hotel acogedor en el centro de la ciudad.",
            address="Calle Principal 123",
        )

    def test_create_property(self):
        self.assertEqual(self.property.name, "Hotel Los Pinos")
        self.assertEqual(self.property.get_property_type_display(), "Hotel")
        self.assertTrue(self.property.is_active)

    def test_property_name_unique(self):
        with self.assertRaises(ValidationError):
            property = Property(name="Hotel Los Pinos", property_type="HOTEL")
            property.full_clean()

    def test_modify_property(self):
        # Modificar la propiedad
        self.property.name = "Hotel Los Alamos"
        self.property.save()
        updated_property = Property.objects.get(id=self.property.id)
        self.assertEqual(updated_property.name, "Hotel Los Alamos")

    def test_delete_property(self):
        # Eliminar la propiedad
        property_id = self.property.id
        self.property.delete()
        with self.assertRaises(Property.DoesNotExist):
            Property.objects.get(id=property_id)

    def test_property_str_method(self):
        # Verificar el método __str__
        self.assertEqual(str(self.property), "Hotel Los Pinos (Hotel)")

    def test_property_with_rooms(self):
        # Verificar relación con habitaciones
        from rooms.models import Room

        # Crear algunas habitaciones para esta propiedad
        Room.objects.create(
            property=self.property,
            name="101",
            room_type="PRIVATE_ROOM",
            capacity=2,  # noqa
        )
        Room.objects.create(
            property=self.property,
            name="102",
            room_type="PRIVATE_ROOM",
            capacity=2,  # noqa
        )

        # Verificar que la propiedad tiene habitaciones
        self.assertEqual(self.property.rooms.count(), 2)

        # Verificar que podemos acceder a las habitaciones desde la propiedad
        room_names = list(self.property.rooms.values_list("name", flat=True))
        self.assertIn("101", room_names)
        self.assertIn("102", room_names)

    def test_cascade_delete(self):
        # Verificar que al eliminar una propiedad se eliminan sus habitaciones
        from rooms.models import Room

        # Crear una habitación para esta propiedad
        room = Room.objects.create(
            property=self.property,
            name="101",
            room_type="PRIVATE_ROOM",
            capacity=2,  # noqa
        )

        # Guardar el ID de la habitación
        room_id = room.id

        # Eliminar la propiedad
        self.property.delete()

        # Verificar que la habitación también se eliminó
        with self.assertRaises(Room.DoesNotExist):
            Room.objects.get(id=room_id)
