from rest_framework import serializers

from .models import Room


class RoomSerializer(serializers.ModelSerializer):
    property = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Room
        fields = [
            "id",
            "property",
            "name",
            "room_type",
            "capacity",
            "base_price",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
