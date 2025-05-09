from rest_framework import serializers

from .models import Room


class RoomSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Room
        fields = [
            "id",
            "property",
            "name",
            "room_type",
            "capacity",
            "base_price",
            "is_active",
            "description",
        ]  # Especifica los campos necesarios
        extra_kwargs = {
            "property_name": {"required": True},
            "room_type": {"required": True},
            "room_number": {"required": True},
            "price_per_night": {"required": True},
            "availability_status": {"required": True},
            "description": {"required": False},  # Este campo es opcional
        }
