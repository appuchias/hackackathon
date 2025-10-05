from datetime import datetime

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_not_required

from hackudc.forms import ParticipanteForm, Registro, PaseForm, PresenciaForm
from hackudc.models import Mentor, Participante, Pase, Persona, Presencia, TipoPase


@login_not_required
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


def gestion(request: HttpRequest):
    return render(request, "gestion/index.html")


@csrf_exempt  # Revisar. ¿Por qué no funciona el csrf en hackudc.local.delthia.com?
@require_http_methods(["GET", "POST"])
def alta(request: HttpRequest):
    """Check-in del evento. Asocia un participante a una acreditación

    1. Se devuelve la página con el formulario
    2. Petición post con el correo del participante. Devuelve los datos
    3. Petición post con el participante y la acreditación. Se asigna en la base de datos
    """
    # 1. Formulario de registro vacío
    if request.method == "GET":
        return render(request, "gestion/registro.html", {"form": Registro()})

    form = Registro(request.POST)

    if form.is_valid():
        datos = form.cleaned_data

        persona = Persona.objects.filter(correo=datos["correo"]).first()

        if not persona:
            messages.error(request, "No se encontró el participante")
            return redirect("alta")

        if not persona.aceptado:
            messages.error(request, "El participante no ha sido aceptado")
            return redirect("alta")

        if persona.acreditacion:
            messages.error(request, "El participante ya está registrado")
            return redirect("alta")

        # 2. Petición solo con el correo
        # Mostrar los datos y el formulario precompletado con el correo
        if not datos["acreditacion"]:
            messages.info(request, f"{persona.nombre} - {persona.talla_camiseta}")
            return render(request, "gestion/registro.html", {"form": form})

        # 3. Petición completa
        # Asignar la acreditación. Página de éxito con timeout y volver a la original
        persona.acreditacion = datos["acreditacion"]
        persona.save()

        messages.success(
            request,
            f"Asignada acreditación {persona.acreditacion} a {persona.correo}",
        )
        return redirect("alta")


@require_http_methods(["GET", "POST"])
def pases(request: HttpRequest):
    """Pases del evento. Registra un pase y muestra si es la primera vez que ese participante utiliza ese pase"""

    if not (TipoPase.objects.filter(inicio_validez__lte=datetime.now()).exists()):
        messages.error(
            request, "No hay pases disponibles. Crea uno en el panel de administración."
        )
        return render(request, "gestion/pases.html", {"form": PaseForm()})

    if request.method == "GET":
        return render(request, "gestion/pases.html", {"form": PaseForm()})

    form = PaseForm(request.POST)

    if form.is_valid():
        datos = form.cleaned_data
        persona = Persona.objects.get(acreditacion=datos["acreditacion"])

        if persona:
            pase = Pase(persona=persona, tipo_pase=datos["tipo_pase"])
            pase.save()
            messages.success(request, f"Pase creado")
        else:
            messages.error(request, "No existe la acreditación")
    else:
        messages.error(request, "Datos incorrectos")

    return redirect("pases")


@require_http_methods(["GET", "POST"])
def presencia(request: HttpRequest):
    mensaje = None

    if request.method == "POST":
        form = PresenciaForm(request.POST)

        if form.is_valid():
            datos = form.cleaned_data
            persona = Persona.objects.filter(acreditacion=datos["acreditacion"]).first()

            if not persona:
                mensaje = "No existe la acreditación"

            presencias = Presencia.objects.filter(persona=persona)
            ultima = presencias.order_by("entrada").last()

            # Acciones
            match datos["accion"]:
                case "v":
                    ultima = presencias.order_by("entrada").last()
                    return HttpResponse(f"{ultima.entrada} - {ultima.salida}")
                case "e":
                    # Comprobar que salió
                    if not ultima.salida:
                        return HttpResponse("No salió")

                    # Guardar entrada
                    entrada = Presencia(persona=persona, entrada=datetime.now())
                    entrada.save()
                    return HttpResponse("OK")

                case "s":
                    # Comprobar que entró
                    if ultima.salida:
                        return HttResponse("No entró")

                    # Guardar salida
                    ultima.salida = datetime.now()
                    ultima.save()
                    return HttpResponse("OK")

    return render(
        request, "gestion/presencia.html", {"form": PresenciaForm, "mensaje": mensaje}
    )
