from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from gestion import views

urlpatterns = [
    path("", views.registro, name="registro"),
    path("verificar/<token>", views.verificar_correo, name="verificar-correo"),
    path("confirmar/<token>", views.confirmar_plaza, name="confirmar-plaza"),
    path(
        "login",
        LoginView.as_view(template_name="login.html", next_page="gestion"),
        name="login",
    ),
    path("logout", LogoutView.as_view(next_page="login"), name="logout"),
    path("gestion", views.gestion, name="gestion"),
    path("gestion/registro", views.alta, name="alta"),
    path("gestion/pases", views.pases, name="pases"),
    path("gestion/presencia", views.presencia, name="presencia"),
    path("gestion/presencia/<acreditacion>", views.presencia, name="presencia"),
    path(
        "gestion/presencia/<acreditacion>/entrada",
        views.presencia_entrada,
        name="presencia-entrada",
    ),
    path(
        "gestion/presencia/<acreditacion>/salida",
        views.presencia_salida,
        name="presencia-salida",
    ),
    path(
        "gestion/presencia/<id_presencia>/editar",
        views.presencia_editar,
        name="presencia-editar",
    ),
]
