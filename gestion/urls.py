# Copyright (C) 2025-2026  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from gestion import views

urlpatterns = [
    path("", views.registro, {"subclase": "participante"}, name="registro"),
    path("mentores", views.registro, {"subclase": "mentor"}, name="registro-mentores"),
    path("colaboradores", views.colaboradores, name="registro-colaboradores"),
    path("media/cv/<archivo>", views.cvs),
    path("verificar/<token>", views.verificar_correo, name="verificar-correo"),
    path("confirmar/<token>", views.confirmar_plaza, name="confirmar-plaza"),
    path("confirmar/<token>/aceptar", views.aceptar_plaza, name="aceptar-plaza"),
    path("confirmar/<token>/rechazar", views.rechazar_plaza, name="rechazar-plaza"),
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
    path("gestion/info", views.info_participante, name="info-participante"),
    path("gestion/normalizacion", views.normalizacion, name="normalizacion"),
    path("gestion/normalizacion/<campo>", views.normalizacion, name="normalizacion"),
]
