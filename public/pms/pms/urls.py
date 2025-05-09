from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView  # noqa
from django.conf import settings
from rest_framework import routers
from rooms.views import RoomViewSet
from accounts.views import UserViewSet, LoginAPI



router = routers.DefaultRouter()
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("accounts.urls")),
    path('api/', include(router.urls)),
    path('api/auth/', include('knox.urls')),
    path('api/auth/login/', LoginAPI.as_view(), name='knox_login'),
]
