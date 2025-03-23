from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path(
        "",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html",
            redirect_authenticated_user=True,  # noqa
        ),
        name="login",
    ),  # noqa
    path(
        "logout/",
        auth_views.LogoutView.as_view(
            next_page="login", http_method_names=["post", "get"]
        ),
        name="logout",
    ),  # noqa
    path("dashboard/", views.dashboard, name="dashboard"),
]
