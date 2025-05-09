from django.shortcuts import render  # noqa
from rest_framework import permissions, viewsets
from rest_framework.response import Response

from .models import Room
from .serializers import RoomSerializer


class RoomViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows rooms to be viewed or edited.
    """

    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
