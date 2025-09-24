from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from hackudc import views

urlpatterns = [
    path("", views.registro, name="registro"),
    path("gestion", views.gestion, name="gestion"),
    path("gestion/registro", views.alta, name="alta"),
    path("gestion/pases", views.pases, name="pases"),
    path("gestion/presencia", views.presencia, name="presencia"),
]


urlpatterns += [
    path(
        "login",
        LoginView.as_view(template_name="login.html", next_page="gestion"),
        name="login",
    ),
    path("logout", LogoutView.as_view(next_page="login"), name="logout"),
]
