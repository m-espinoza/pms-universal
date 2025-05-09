from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.shortcuts import render
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView
from rest_framework import permissions, viewsets
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.response import Response

from .serializers import GroupSerializer, UserSerializer


@login_required
def dashboard(request):
    return render(request, "accounts/dashboard.html")


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token = AuthToken.objects.create(user)[1]
        return Response({"user": UserSerializer(user).data, "token": token})
