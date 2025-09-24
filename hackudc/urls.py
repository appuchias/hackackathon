from django.urls import path

from hackudc import views

urlpatterns = [
    path("", views.registro, name="registro"),
    path("gestion", views.gestion, name="gestion"),
    path("gestion/registro", views.alta, name="alta"),
    path("gestion/pases", views.pases, name="pases"),
    path("gestion/presencia", views.presencia, name="presencia"),
]
