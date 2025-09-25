from datetime import datetime

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

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


@csrf_exempt  # Revisar. ¿Por qué no funciona el csrf en hackudc.local.delthia.com?
def alta(request: HttpRequest):
    """Check-in del evento. Asocia un participante a una acreditación

    1. Se devuelve la página con el formulario
    2. Petición post con el correo del participante. Devuelve los datos
    3. Petición post con el participante y la acreditación. Se asigna en la base de datos
    """
    form = Registro

    # 2 y 3. Post con el formulario
    if request.method == "POST":
        form = Registro(request.POST)

        if form.is_valid():
            datos = form.cleaned_data
            participante = Participante.objects.filter(correo=datos["persona"]).first()

            # Gestión de errores
            # Volver a la página original mostrando el mensaje de error
            if not participante:
                return HttpResponse("No se encontró el participante")
            elif not participante.aceptado:
                return HttpResponse("Participante no aceptado")
            elif participante.uuid:
                return HttpResponse("Ya registrado")

            # 2. Petición solo con el correo
            # Mostrar los datos y el formulario precompletado con el correo
            if not datos["acreditacion"]:
                return render(
                    request,
                    "gestion/registro.html",
                    {
                        "form": form,
                        "mensaje": f"{participante.nombre} - {participante.talla_camiseta}",
                    },
                )

            # 3. Petición completa
            # Asignar la acreditación. Página de éxito con timeout y volver a la original
            participante.uuid = datos["acreditacion"]
            participante.save()

            return HttpResponse(
                f"Asignada acreditación <b>{participante.uuid}</b> a <b>{participante.correo}</b>"
            )

    # 1. Formulario de registro vacío
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

    if action == "ver":
        ultima = presencias.order_by("entrada").last()
        return HttpResponse(f"{ultima.entrada} - {ultima.salida}")

    ultima = presencias.order_by("entrada").last()
    if action == "entrada":
        # Comprobar que salió
        if not ultima.salida:
            return HttpResponse("No salió")

        # Guardar entrada
        participante = Participante.objects.filter(correo=uuid).first()
        entrada = Presencia(participante=participante, entrada=datetime.now())
        entrada.save()
        return HttpResponse("OK")
    elif action == "salida":
        # Comprobar que entró
        if ultima.salida:
            return HttpResponse("No entró")

        # Guardar salida
        ultima.salida = datetime.now()
        ultima.save()
        return HttpResponse("OK")
