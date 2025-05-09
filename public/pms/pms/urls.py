from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView  # noqa
from rest_framework import routers

from accounts.views import LoginAPI, UserViewSet
from rooms.views import RoomViewSet

router = routers.DefaultRouter()
router.register(r"rooms", RoomViewSet, basename="room")
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("accounts.urls")),
    path("api/", include(router.urls)),
    path("api/auth/", include("knox.urls")),
    path("api/auth/login/", LoginAPI.as_view(), name="knox_login"),
]
