from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from hackudc.forms import ParticipanteForm, Registro
from hackudc.models import Participante


# Create your views here.
@require_http_methods(["GET", "POST"])
def registro(request: HttpRequest):
    if request.method == "GET":
        return render(request, "registro.html", {"form": ParticipanteForm()})

    form = ParticipanteForm(request.POST, request.FILES)
    if form.is_valid():
        form.save()
        return HttpResponse("OK")
    else:
        return render(request, "registro.html", {"form": form})


# /gestion/
def gestion(request: HttpRequest):
    return render(request, "gestion/index.html")


def alta(request: HttpRequest):
    form = Registro

    if request.method == "POST":
        form = Registro(request.POST)
        if form.is_valid():
            participante = Participante.objects.filter(
                correo=form.cleaned_data["persona"]
            ).first()
            participante.uuid = form.cleaned_data["acreditacion"]

            participante.save()
            return HttpResponse(participante.nombre + "-" + participante.talla_camiseta)

    return render(request, "gestion/registro.html", {"form": form})


def pases(request: HttpRequest):
    return render(request, "gestion/pases.html")


def presencia(request: HttpRequest):
    return render(request, "gestion/presencia.html")
