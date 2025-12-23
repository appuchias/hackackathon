from django.urls import include, path
from rest_framework import routers

from api import views

router = routers.DefaultRouter()

# Usamos enrutamiento automático
# Añadimos la ruta de login para la interfaz web
urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("rest_framework.urls", namespace="rest_framework")),
]
