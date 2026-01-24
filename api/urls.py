# Copyright (C) 2025-now  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

from django.urls import include, path
from rest_framework import routers

from api import views

router = routers.DefaultRouter()
router.register(r"tipo_pase", views.TipoPaseViewSet, basename="tipo_pase")
router.register(r"pase", views.PaseViewSet, basename="pase")
router.register(r"presencia", views.PresenciaViewSet, basename="presencia")


urlpatterns = [
    path("", include(router.urls)),
    # Ruta de login para la interfaz web
    path("auth/", include("rest_framework.urls", namespace="rest_framework")),
]

urlpatterns += [
    path("persona", views.PersonaList.as_view()),
    path("persona/<correo>/", views.PersonaRetrieveUpdate.as_view()),
    # path("presencia/<acreditacion>/<accion>", views.PresenciaAccion.as_view()),
]
