# Copyright (C) 2025-now  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_not_required
from django.core.mail import EmailMultiAlternatives
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from gestion.forms import EditarPresenciaForm, ParticipanteForm, PaseForm, Registro
from gestion.models import Participante, Pase, Persona, Presencia, TipoPase, Token

EMAIL_VERIFICACION_ASUNTO = "HackUDC 2026 - Confirma tu correo ✉️"
EMAIL_CONFIRMACION_ASUNTO = "HackUDC 2026 - Confirma tu plaza! <emoji>"


@login_not_required
@require_http_methods(["GET", "POST"])
def registro(request: HttpRequest):
    if timezone.now() > datetime.fromisoformat(settings.PLAZO_REGISTRO):
        return render(request, "registro_cerrado.html")

    if request.method == "GET":
        return render(request, "registro.html", {"form": ParticipanteForm()})

    form = ParticipanteForm(request.POST, request.FILES)
    if form.is_valid():
        participante: Participante = form.save()
        token = Token(
            tipo="VERIFICACION",
            persona=participante,
            fecha_expiracion=timezone.now() + timedelta(days=7),
        )
        token.save()
        try:
            params = {
                "nombre": participante.nombre,
                "token": token.token,
                "host": request.get_host(),
            }
            email = EmailMultiAlternatives(
                EMAIL_VERIFICACION_ASUNTO,
                render_to_string("correo/....txt", params),
                to=(participante.correo,),
                reply_to=("info@gpul.org",),
                headers={"Message-ID": f"hackudc-{token.fecha_creacion.timestamp()}"},
            )
            email.attach_alternative(
                render_to_string("correo/....html", params), "text/html"
            )
            email.send(fail_silently=False)
        except ConnectionRefusedError:
            messages.error(
                request,
                "Error al mandar el correo. Inténtalo más tarde o contacta con nosotros a través de hackudc@gpul.org",
            )
            return render(request, "registro.html", {"form": form})

        messages.success(
            request, "Registro completado. Revisa tu correo para verificarte!"
        )
        return redirect("registro")

    messages.error(request, "Datos incorrectos")
    return render(request, "registro.html", {"form": form})


@login_not_required
@require_http_methods(["GET"])
def verificar_correo(request: HttpRequest, token: str):
    token_obj = Token.objects.filter(token=token, tipo="VERIFICACION").first()
    if not token_obj:
        messages.error(request, "El token es inválido.")
        return render(
            request,
            "verificacion_incorrecta.html",
            {"motivo": "Token inválido", "token": token},
        )

    if not token_obj.valido():
        messages.error(
            request,
            "El token de verificación ha expirado.",
        )
        return render(
            request,
            "verificacion_incorrecta.html",
            {"motivo": "Token expirado", "token": token},
        )

    ahora = timezone.now()

    participante: Participante = Participante.objects.get(
        correo=token_obj.persona.correo
    )
    participante.fecha_verificacion_correo = ahora
    participante.save()

    token_obj.fecha_uso = ahora

    messages.success(request, "Correo verificado correctamente")
    return render(request, "verificacion_correcta.html", {"participante": participante})


@login_not_required
@require_http_methods(["GET", "POST"])
def confirmar_plaza(request: HttpRequest, token: str):
    token_obj = Token.objects.filter(token=token, tipo="CONFIRMACION").first()
    if not token_obj:
        messages.error(request, "Token inválido")
        return redirect("registro")

    if not token_obj.valido():
        messages.error(
            request,
            "El token de verificación ha expirado. Ponte en contacto con nosotros para confirmar tu plaza a través de hackudc@gpul.org.",
        )
        return redirect("registro")

    if request.method == "POST":
        ahora = timezone.now()

        participante: Participante = Participante.objects.get(
            correo=token_obj.persona.correo
        )
        participante.fecha_confirmacion_plaza = ahora
        participante.save()

        token_obj.fecha_uso = ahora
        token_obj.save()

        return HttpResponse("Pues ya estás aceptado")

    # return HttpResponse(
    #     f"Hola {token}, tienes hasta {token_obj.fecha_expiracion} para confirmar tu plaza"
    # )
    # print(type(datetime.now()))
    # print(datetime.now())
    # print(type(token_obj.fecha_expiracion))
    # print(token_obj.fecha_expiracion)
    # rprint(datetime.now(timezone.utc) - token_obj.fecha_expiracion)
    return render(
        request,
        "confirmar-plaza.html",
        {
            "token": token_obj,
            # "restante": datetime.utcnow() - token_obj.fecha_expiracion,
        },
    )


def gestion(request: HttpRequest):
    return render(request, "gestion/index.html")


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

        if persona.fecha_aceptacion is None:
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

    messages.error(request, "Datos incorrectos")
    return render(request, "gestion/registro.html", {"form": form})


@require_http_methods(["GET", "POST"])
def pases(request: HttpRequest):
    """Pases del evento. Registra un pase y muestra si es la primera vez que ese participante utiliza ese pase"""

    if not (TipoPase.objects.filter(inicio_validez__lte=timezone.now()).exists()):
        messages.error(
            request, "No hay pases disponibles. Crea uno en el panel de administración."
        )
        return render(request, "gestion/pases.html", {"form": PaseForm()})

    if request.method == "GET":
        return render(request, "gestion/pases.html", {"form": PaseForm()})

    form = PaseForm(request.POST)

    if form.is_valid():
        datos = form.cleaned_data
        persona = Persona.objects.filter(acreditacion=datos["acreditacion"]).first()

        if persona:
            pase = Pase(persona=persona, tipo_pase=datos["tipo_pase"])
            pase.save()
            messages.success(request, f"Pase creado")
            return redirect("pases")

        messages.error(request, "No existe la acreditación")
        return render(request, "gestion/pases.html", {"form": PaseForm()})

    messages.error(request, "Datos incorrectos")
    return render(request, "gestion/pases.html", {"form": form})


@require_http_methods(["GET"])
def presencia(request: HttpRequest, acreditacion: str = ""):
    if not acreditacion:
        acreditacion = request.GET.get("acreditacion", "")

    if not acreditacion:
        return render(request, "gestion/presencia.html")

    persona = Persona.objects.filter(acreditacion=acreditacion).first()

    if not persona:
        messages.error(request, "No existe la acreditación")
        return redirect("presencia")

    presencias = Presencia.objects.filter(persona=persona).order_by("-entrada")

    tiempo_total = timedelta()
    for presencia in presencias:
        if presencia.entrada and presencia.salida:
            tiempo_total += presencia.salida - presencia.entrada

    tiempo_total = str(tiempo_total).split(".")[0]  # Remove microseconds

    if not presencias.exists():
        messages.warning(request, "No hay presencias registradas")

    presencias_sin_entrada = presencias.filter(entrada__isnull=True).exists()

    return render(
        request,
        "gestion/presencia.html",
        {
            "persona": persona,
            "presencias": presencias,
            "presencias_sin_entrada": presencias_sin_entrada,
            "tiempo_total": tiempo_total,
        },
    )


@require_http_methods(["GET"])
def presencia_entrada(request: HttpRequest, acreditacion: str):
    persona = Persona.objects.filter(acreditacion=acreditacion).first()
    if not persona:
        messages.error(request, "No existe la acreditación")
        return redirect("presencia")

    presencias = Presencia.objects.filter(persona=persona)
    ultima = presencias.order_by("-entrada").first()

    if not ultima:
        messages.error(request, "No había ninguna entrada")
    elif not ultima.salida:
        messages.warning(request, "No hay salida registrada de la última presencia")

    # Guardar entrada
    entrada = Presencia(persona=persona, entrada=timezone.now())
    entrada.save()

    return redirect("presencia", acreditacion=acreditacion)


@require_http_methods(["GET"])
def presencia_salida(request: HttpRequest, acreditacion: str):
    persona = Persona.objects.filter(acreditacion=acreditacion).first()
    if not persona:
        messages.error(request, "No existe la acreditación")
        return redirect("presencia")

    presencias = Presencia.objects.filter(persona=persona)
    ultima = presencias.order_by("-entrada").first()

    if not ultima:
        messages.error(request, "No había ninguna entrada")
        ultima = Presencia(persona=persona)
    elif ultima.salida:
        messages.warning(request, "La última presencia ya tiene salida registrada")
        ultima = Presencia(persona=persona)

    # Guardar salida
    ultima.salida = timezone.now()
    ultima.save()

    return redirect("presencia", acreditacion=acreditacion)


@require_http_methods(["GET", "POST"])
def presencia_editar(request: HttpRequest, id_presencia: str):
    presencia = Presencia.objects.filter(id_presencia=id_presencia).first()
    if not presencia:
        messages.error(request, "No existe la presencia")
        return redirect("presencia")

    if request.method == "GET":
        return render(
            request,
            "gestion/editar_presencia.html",
            {"presencia": presencia, "form": EditarPresenciaForm(instance=presencia)},
        )

    # POST
    form = EditarPresenciaForm(request.POST, instance=presencia)
    if form.is_valid():
        form.save()
        messages.success(request, "Presencia actualizada")
        return redirect("presencia", acreditacion=presencia.persona.acreditacion)

    messages.error(request, "Datos incorrectos")
    return render(
        request,
        "gestion/editar_presencia.html",
        {"presencia": presencia, "form": form},
    )

