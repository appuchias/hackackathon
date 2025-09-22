from django.urls import path

from hackudc import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("registro", views.registro, name="registro"),
    path("ruta", views.ruta, name="ruta"),
    path("gestion", views.gestion, name="gestion"),
    path("gestion/registro", views.alta, name="registro"),
    path("gestion/pases", views.pases, name="pases"),
    path("gestion/presencia", views.presencia, name="presencia")
]
