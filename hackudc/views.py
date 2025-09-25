from datetime import datetime

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail

from hackudc.forms import ParticipanteForm, Registro
from hackudc.models import Participante, Token


# Create your views here.
@require_http_methods(["GET", "POST"])
def registro(request: HttpRequest):
    if request.method == "GET":
        return render(request, "registro.html", {"form": ParticipanteForm()})

    form = ParticipanteForm(request.POST, request.FILES)
    if form.is_valid():
        participante = form.save()
        token = Token(persona=participante, fecha=datetime.now())
        token.save()
        print(participante)
        try:
            send_mail(
                "HackUDC 2026 - Confirma tu correo ✉️",
                f"Hola {form.cleaned_data["nombre"]}. Toma tu token {token.uuid}",
                "no-reply@gpul.org",
                (form.cleaned_data["correo"],),
                fail_silently=False,
            )
        except ConnectionRefusedError:
            return HttpResponse(
                "Error al mandar el correo. Inténtalo más tarde o contacta con nosotros a través de hackudc@gpul.org"
            )
        return HttpResponse("OK")
    else:
        return render(request, "registro.html", {"form": form})


def confirmar_correo(request: HttpRequest, token):
    token = Token.objects.filter(uuid=token).first()

    if not token:
        return HttpResponse("No existe el token")

    participante = token.persona
    participante.verificado = True
    participante.save()
    token.delete()

    return HttpResponse("Confirmado")


def confirmar_plaza(request: HttpRequest, token):
    token = Token.objects.filter(uuid=token).first()

    if not token:
        return HttpResponse("No existe el token")

    persona = token.persona
    participante = Participante.objects.filter(correo=persona.correo).first()
    participante.confirmado = True
    participante.save()
    token.delete()

    return HttpResponse("Confirmado")


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
