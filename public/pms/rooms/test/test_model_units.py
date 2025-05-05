from django.core.exceptions import ValidationError
from django.test import TestCase

from rooms.models import Room, Unit, Property


class UnitModelTest(TestCase):
    def setUp(self):
        # Crear primero una propiedad
        self.property = Property.objects.create(
            name="Hotel Example",
            property_type="HOTEL",
            description="A test hotel"
        )
        
        # Configuración común para las pruebas
        self.room = Room.objects.create(
            property=self.property,  # Asociar la habitación a la propiedad
            name="Room 101", 
            room_type="PRIVATE_ROOM"
        )
        
        self.unit = Unit.objects.create(
            name="1", 
            unit_type="SINGLE_BED", 
            room=self.room
        )

    def test_create_unit(self):
        self.assertEqual(self.unit.name, "1")
        self.assertEqual(self.unit.room.name, "Room 101")
        # Verificar la asociación indirecta con la propiedad
        self.assertEqual(self.unit.room.property.name, "Hotel Example")

    def test_unit_number_unique_per_room(self):
        # Probar que el nombre debe ser único por habitación
        with self.assertRaises(ValidationError):
            unit = Unit(name="1", unit_type="SINGLE_BED", room=self.room)
            unit.full_clean()
        
        # Crear una segunda habitación en la misma propiedad
        room2 = Room.objects.create(
            property=self.property,
            name="Room 102", 
            room_type="PRIVATE_ROOM"
        )
        
        # Debería permitir el mismo nombre de unidad en una habitación diferente
        try:
            unit = Unit(name="1", unit_type="SINGLE_BED", room=room2)
            unit.full_clean()
            unit.save()
            self.assertTrue(True)
        except ValidationError:
            self.fail("No debería lanzar ValidationError para mismo nombre en diferente habitación")

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
        
        # Verificar que la habitación y la propiedad siguen existiendo
        self.assertTrue(Room.objects.filter(id=self.room.id).exists())
        self.assertTrue(Property.objects.filter(id=self.property.id).exists())

    def test_property_room_unit_relationship(self):
        # Verificar la cadena de relaciones
        property_from_unit = self.unit.room.property
        self.assertEqual(property_from_unit.id, self.property.id)
        
        # Verificar que podemos navegar desde la propiedad hasta las unidades
        rooms_in_property = self.property.rooms.all()
        self.assertEqual(rooms_in_property.count(), 1)
        
        units_in_first_room = rooms_in_property.first().units.all()
        self.assertEqual(units_in_first_room.count(), 1)
        self.assertEqual(units_in_first_room.first().id, self.unit.id)