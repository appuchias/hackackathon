from datetime import datetime

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from hackudc.forms import ParticipanteForm, Registro
from hackudc.models import Participante, Pase, Presencia, TipoPase


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

            if not participante.aceptado:
                return HttpResponse("Participante no aceptado")
            elif participante.uuid:
                return HttpResponse("Ya se registró")
            participante.uuid = form.cleaned_data["acreditacion"]

            participante.save()
            return HttpResponse(participante.nombre + "-" + participante.talla_camiseta)

    return render(request, "gestion/registro.html", {"form": form})


def pases(request: HttpRequest):
    # return render(request, "gestion/pases.html")
    actual = (
        TipoPase.objects.filter(inicio_validez__lte=datetime.now())
        .order_by("inicio_validez")
        .last()
    )

    return HttpResponse(actual)


def presencia(request: HttpRequest, uuid: str, action: str):
    participante = Participante.objects.filter(uuid=uuid).first()
    presencias = Presencia.objects.filter(participante=participante)

    if action == 'ver':
        ultima = presencias.order_by("entrada").last()
        return HttpResponse(f"{ultima.entrada} - {ultima.salida}")

    ultima = presencias.order_by("entrada").last()
    if action == 'entrada':
        # Comprobar que salió
        if not ultima.salida:
            return HttpResponse("No salió")

        # Guardar entrada
        participante = Participante.objects.filter(correo=uuid).first()
        entrada = Presencia(participante=participante, entrada=datetime.now())
        entrada.save()
        return HttpResponse("OK")
    elif action == 'salida':
        # Comprobar que entró
        if ultima.salida:
            return HttpResponse("No entró")

        # Guardar salida
        ultima.salida = datetime.now()
        ultima.save()
        return HttpResponse("OK")
