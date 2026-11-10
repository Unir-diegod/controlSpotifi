from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "control"

urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="control/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("integrantes/", views.members, name="members"),
    path("pagos/", views.payments, name="payments"),
    path("reportes/", views.reports, name="reports"),
]
