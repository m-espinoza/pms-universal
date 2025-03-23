from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView  # noqa

from accounts import urls  # noqa

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("accounts.urls")),
]
