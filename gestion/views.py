# Copyright (C) 2025-2026  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

import logging, os
from datetime import timedelta
from uuid import UUID

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_not_required
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMultiAlternatives
from django.db import IntegrityError
from django.http import FileResponse, HttpRequest, HttpResponse
from django.shortcuts import Http404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from gestion.forms import (
    ColaboradorForm,
    ConsultaForm,
    EditarPresenciaForm,
    MentorForm,
    NormalizacionForm,
    ParticipanteForm,
    PaseForm,
    Registro,
    RevisarMentorForm,
    RevisarParticipanteForm,
)
from gestion.models import (
    Colaborador,
    Mentor,
    Participante,
    Pase,
    Persona,
    Presencia,
    TipoPase,
    Token,
)
from gestion.utils import (
    enviar_correo_aceptacion_plaza,
    enviar_correo_colaborador,
    enviar_correo_rechazo_plaza,
    enviar_correo_verificacion,
    enviar_correo_verificacion_correcta,
)

logger = logging.getLogger(__name__)

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter())
)


def es_token(token: str) -> bool:
    try:
        UUID("{" + token + "}", version=4)
        return True

    except ValueError:
        return False


@login_not_required
@require_http_methods(["GET", "POST"])
def registro(request: HttpRequest, *args, **kwargs):
    if timezone.now() > settings.FECHA_FIN_REGISTRO:
        logger.debug("Intento de acceso con el registro cerrado")
        return render(request, "registro_cerrado.html")

    if kwargs.get("subclase") == "participante":
        titulo = "Regístrate para participar en"
        url = reverse("registro")
        subclase = Participante
        subform = ParticipanteForm
    elif kwargs.get("subclase") == "mentor":
        titulo = "Regístrate como mentor en"
        url = reverse("registro-mentores")
        subclase = Mentor
        subform = MentorForm
    else:
        raise ValueError("El valor de subclase debe ser 'participante' o 'mentor'.")

    if request.method == "GET":
        return render(
            request,
            "registro.html",
            {"form": subform(), "titulo": titulo, "url_form": url},
        )

    form = subform(request.POST, request.FILES)
    if form.is_valid() and request.POST.get("acepta_terminos", False):
        persona: subclase = form.save()

        estado = enviar_correo_verificacion(persona)
        if estado != 0:
            messages.error(
                request,
                "Error al enviar el correo de verificación. Contacta con nosotros a través de hackudc@gpul.org para resolverlo.",
            )
            return render(
                request,
                "registro.html",
                {"form": form, "titulo": titulo, "url_form": url},
            )

        return render(
            request,
            "registro.html",
            {"form": form, "titulo": titulo, "url_form": url, "persona": persona},
        )

    logger.info("Formulario entregado con datos incorrectos.")
    messages.error(request, "Datos incorrectos")
    return render(
        request, "registro.html", {"form": form, "titulo": titulo, "url_form": url}
    )


@login_not_required
@require_http_methods(["GET", "POST"])
def colaboradores(request: HttpRequest):
    titulo = "Alta de colaboradores para"
    if request.method == "GET":
        return render(
            request,
            "colaboradores.html",
            {"form": ColaboradorForm(), "titulo": titulo},
        )

    form = ColaboradorForm(request.POST)
    if form.is_valid() and request.POST.get("acepta_terminos", False):
        colaborador = form.save()

        estado = enviar_correo_colaborador(colaborador)
        if estado != 0:
            messages.error(
                request,
                "Error enviando el correo electrónico. Contacta con nosotros a través de hackudc@gpul.org para confirmar que la solicitud se registró correctamente.",
            )
            return render(
                request, "colaboradores.html", {"form": form, "titulo": titulo}
            )
        return render(
            request,
            "colaboradores.html",
            {
                "form": form,
                "titulo": titulo,
                "colaborador": colaborador,
            },
        )

    logger.info("Formulario entregado con datos incorrectos.")
    messages.error(request, "Datos incorrectos")
    return render(request, "registro.html", {"form": form, "titulo": titulo})


@login_not_required
@require_http_methods(["GET"])
def verificar_correo(request: HttpRequest, token: str):
    if not es_token(token):
        logger.debug(f"Token inválido '{token}'")
        messages.error(
            request, "El token es inválido. Comprueba que copiaste el enlace completo"
        )
        return render(
            request,
            "verificacion_incorrecta.html",
            {"motivo": "Token inválido", "token": token},
        )

    token_obj = Token.objects.filter(token=token, tipo="VERIFICACION").first()
    if not token_obj:
        logger.debug(f"Token inválido '{token}'")
        messages.error(request, "El token es inválido.")
        return render(
            request,
            "verificacion_incorrecta.html",
            {"motivo": "Token inválido", "token": token},
        )

    persona = Persona.objects.get(correo=token_obj.persona.correo)

    if persona.tipo() == "Participante":
        subpersona = persona.participante
        form = RevisarParticipanteForm
    elif persona.tipo() == "Mentor":
        subpersona = persona.mentor
        form = RevisarMentorForm
    else:
        raise ValueError("La persona no es un participante ni un mentor")

    # No permitir verificar el correo si el Token ha expirado
    if not token_obj.valido() and not persona.verificado():
        logger.debug(f"Token expirado '{token}'", extra={"correo": persona.correo})
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

    # Actualizar la fecha de uso del Token aunque la Persona ya esté verificada con otro Token
    if not token_obj.usado():
        token_obj.fecha_uso = ahora
        token_obj.save()

    # Verificar a la Persona la primera vez que usa un Token de verificación
    if not persona.verificado():
        persona.fecha_verificacion_correo = ahora
        persona.save()

        estado = enviar_correo_verificacion_correcta(persona)
        if estado != 0:
            logger.error(
                f"Error al enviar el correo de que verificó su correo a {persona.correo}"
            )
            messages.error(
                request, "Error al enviar el correo de verificación correcta."
            )

        logger.info(
            f"Una persona ha verificado su correo.",
            extra={"correo": persona.correo},
        )
        messages.success(
            request,
            "Tu correo está verificado! Vuelve cuando quieras para revisar tus detalles!",
        )
        return render(
            request,
            "verificacion_correcta.html",
            {"persona": persona, "form": form(instance=subpersona)},
        )

    logger.debug(
        f"Una persona ha revisado sus datos.", extra={"correo": persona.correo}
    )

    if (
        persona.fecha_aceptacion
        and not persona.fecha_confirmacion_plaza
        and not persona.fecha_rechazo_plaza
    ):
        messages.warning(
            request, "Estás aceptado! Revisa tu correo para confirmar tu plaza."
        )
    elif (
        persona.fecha_aceptacion
        and persona.fecha_confirmacion_plaza
        and not persona.fecha_rechazo_plaza
    ):
        messages.warning(request, "Tu plaza está confirmada!")
    elif persona.fecha_aceptacion and persona.fecha_rechazo_plaza:
        messages.error(request, "Rechazaste tu plaza.")
    else:
        messages.info(
            request,
            "Ya habías verificado tu correo. Recibirás más información en breve",
        )
    return render(
        request,
        "verificacion_correcta.html",
        {
            "form": form(instance=subpersona),
        },
    )


@login_not_required
@require_http_methods(["GET", "POST"])
def confirmar_plaza(request: HttpRequest, token: str):
    if not es_token(token):
        logger.debug(f"Token inválido '{token}'")
        messages.error(
            request, "El token es inválido. Comprueba que copiaste el enlace completo"
        )
        return render(
            request,
            "verificacion_incorrecta.html",
            {"motivo": "Token inválido", "token": token},
        )

    token_obj = Token.objects.filter(token=token, tipo="CONFIRMACION").first()

    if not token_obj:
        logger.debug(f"Token inválido '{token}'")
        messages.error(request, "Token inválido")
        return render(request, "vacio.html", {"titulo": "Confirmar plaza"})

    participante: Participante = Participante.objects.get(
        correo=token_obj.persona.correo
    )

    token_verificacion = Token.objects.get(
        persona__correo=participante.correo, tipo="VERIFICACION"
    )

    if request.method == "GET":
        return render(
            request,
            "confirmar_plaza.html",
            {
                "token": token_obj,
                "participante": participante,
                "token_verificacion": token_verificacion,
            },
        )

    if not token_obj.valido() and not participante.confirmado():
        logger.debug(f"Token expirado '{token}'", extra={"correo": participante.correo})
        messages.error(
            request,
            "El token de verificación ha caducado. Ponte en contacto con nosotros para confirmar tu plaza a través de hackudc@gpul.org.",
        )

    return render(request, "vacio.html", {"titulo": "Confirmar plaza"})


@login_not_required
@require_http_methods(["POST"])
def aceptar_plaza(request: HttpRequest, token: str):
    token_obj = Token.objects.filter(token=token, tipo="CONFIRMACION").first()

    if not token_obj.valido():
        logger.debug(
            f"Token expirado '{token}'"
        )  # , extra={"correo": participante.correo})
        messages.error(
            request,
            "Token caducado. No puedes confirmar tu plaza. Si crees que es un error, ponte en contacto a través de hackudc@gpul.org para solucionarlo",
        )
        return redirect("confirmar-plaza", token)

    participante: Participante = Participante.objects.get(
        correo=token_obj.persona.correo
    )

    ahora = timezone.now()

    participante.fecha_confirmacion_plaza = ahora
    participante.save()

    token_obj.fecha_uso = ahora
    token_obj.save()

    # Correo confirmación de aceptación
    estado = enviar_correo_aceptacion_plaza(participante)
    if estado != 0:
        logger.error(
            f"Error al enviar el correo de que aceptó su plaza a {participante.correo}"
        )
        messages.error(request, "Error al enviar el correo de que aceptaste la plaza.")

    logger.info(
        f"Un participante ha aceptado su plaza.",
        extra={"correo": participante.correo},
    )
    messages.success(request, "Plaza confirmada.")
    return redirect("confirmar-plaza", token)


@login_not_required
@require_http_methods(["GET", "POST"])
def rechazar_plaza(request: HttpRequest, token: str):
    token_obj = Token.objects.filter(token=token, tipo="CONFIRMACION").first()

    if not token_obj:
        logger.debug(f"Token inválido '{token}'")
        messages.error(request, "Token inválido")
        return render(request, "vacio.html")

    if request.method == "GET":
        return render(request, "rechazar_plaza.html", {"token": token_obj})

    ahora = timezone.now()

    participante: Participante = Participante.objects.get(
        correo=token_obj.persona.correo
    )
    participante.fecha_rechazo_plaza = ahora
    participante.save()

    token_obj.fecha_uso = ahora
    token_obj.save()

    # Correo confirmación de rechazo
    estado = enviar_correo_rechazo_plaza(participante)
    if estado != 0:
        logger.error(
            f"Error al enviar el correo de que rechazó su plaza a {participante.correo}"
        )

        messages.error(request, "Error al enviar el correo de que rechazaste la plaza.")

    logger.info(
        f"Un participante ha rechazado su plaza.",
        extra={"correo": participante.correo},
    )
    messages.success(
        request,
        "Has rechazado tu plaza. Si te arrepientes, contáctanos en hackudc@gpul.org",
    )
    return redirect("confirmar-plaza", token)


def gestion(request: HttpRequest):
    return render(request, "gestion/index.html")


def cvs(request: HttpRequest, archivo: str):
    if not request.user.has_perm("gestion.ver_cv_participante"):
        raise PermissionDenied

    ruta = os.path.join(settings.MEDIA_ROOT, "cv", archivo)

    if not os.path.exists(ruta) or not os.path.isfile(ruta):
        raise Http404("File not found")

    logger.info(
        f"Mostrando el CV {archivo} de un participante a {request.user.username}"
    )

    return FileResponse(open(ruta, "rb"), as_attachment=False)


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

        persona = Persona.objects.filter(correo=datos["persona"]).first()

        context = None

        if not persona:
            context = {"error": "No se encontró al participante", "form": Registro()}
        elif persona.fecha_aceptacion is None:
            context = {"error": "Participante no aceptado", "form": Registro()}
        elif persona.acreditacion:
            context = {"error": "Participante ya registrado", "form": Registro()}
        elif persona.fecha_confirmacion_plaza is None:
            context = {
                "error": "El participante no confirmó su plaza",
                "form": Registro(),
            }
        elif persona.fecha_rechazo_plaza is not None:
            context = {"error": "El participante rechazó su plaza", "form": Registro()}

        if context:
            return render(request, "gestion/registro.htmx.html", context)

        # 2. Petición solo con el correo
        # Mostrar los datos y el formulario precompletado con el correo
        if not datos["acreditacion"]:
            restricciones = persona.restricciones_alimentarias.all()
            return render(
                request,
                "gestion/registro.htmx.html",
                {"persona": persona, "form": form, "restricciones": restricciones},
            )

        # 3. Petición completa
        # Asignar la acreditación. Página de éxito con timeout y volver a la original
        persona.acreditacion = datos["acreditacion"]
        try:
            persona.save()
        except IntegrityError:
            data = form.cleaned_data
            data["acreditacion"] = None
            form = Registro(data)
            return render(
                request,
                "gestion/registro.htmx.html",
                {"persona": persona, "form": form, "error": "Acreditación repetida"},
            )

        # Crear la Presencia inicial del participante
        if not Presencia.objects.filter(persona=persona).exists():
            Presencia(persona=persona, entrada=settings.FECHA_INICIO_EVENTO).save()

        return render(
            request,
            "gestion/registro.htmx.html",
            {"persona": persona, "form": Registro(), "exito": "Acreditacion asignada"},
        )

    return render(
        request,
        "gestion/registro.htmx.html",
        {"error": "Datos incorrectos", "form": Registro()},
    )


@require_http_methods(["GET", "POST"])
def pases(request: HttpRequest):
    """Pases del evento. Registra un pase y muestra si es la primera vez que ese participante utiliza ese pase"""

    if not (TipoPase.objects.filter(inicio_validez__lte=timezone.now()).exists()):
        messages.error(
            request, "No hay pases disponibles. Crea uno en el panel de administración."
        )
        return render(request, "gestion/pases.html", {"form": PaseForm()})

    if request.method == "GET":
        return render(
            request,
            (
                "gestion/pases.htmx.html"
                if request.GET.get("htmx") == "true"
                else "gestion/pases.html"
            ),
            {
                "form": PaseForm(),
                "pase": TipoPase.objects.filter(inicio_validez__lte=timezone.now())
                .order_by("inicio_validez")
                .first(),
                "limpia": True,
            },
        )

    form = PaseForm(request.POST)

    if form.is_valid():
        datos = form.cleaned_data
        persona = Persona.objects.filter(acreditacion=datos["acreditacion"]).first()

        if not persona:
            return render(
                request,
                "gestion/pases.htmx.html",
                {
                    "form": PaseForm(),
                    "pase": TipoPase.objects.filter(inicio_validez__lte=timezone.now())
                    .order_by("inicio_validez")
                    .first(),
                    "error": True,
                },
            )

        pases = Pase.objects.filter(
            persona=persona, tipo_pase=datos["tipo_pase"]
        ).count()

        if datos["confirmar"]:
            pase = Pase(persona=persona, tipo_pase=datos["tipo_pase"])
            pase.save()
            return render(
                request,
                "gestion/pases.htmx.html",
                {
                    "form": PaseForm(),
                    "pase": TipoPase.objects.filter(inicio_validez__lte=timezone.now())
                    .order_by("inicio_validez")
                    .first(),
                    "limpia": True,
                },
            )
        else:
            data = form.data.copy()
            data["confirmar"] = True
            form.data = data
            return render(
                request, "gestion/pases.htmx.html", {"pases": pases, "form": form}
            )

    return render(
        request,
        "gestion/pases.htmx.html",
        {"form": form, "error": "Datos incorrectos"},
    )


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


@require_http_methods(["GET", "POST"])
def info_participante(request: HttpRequest):
    if request.method == "GET":
        return render(request, "gestion/consulta.html", {"form": ConsultaForm})

    form = ConsultaForm(request.POST)

    if form.is_valid():
        # persona = Persona.objects.filter(correo=correo).first()

        datos = form.cleaned_data

        if datos["persona"]:
            persona = Persona.objects.filter(correo=datos["persona"]).first()
        elif datos["acreditacion"]:
            persona = Persona.objects.filter(acreditacion=datos["acreditacion"]).first()
        else:
            return render(
                request,
                "gestion/consulta.html",
                {"error": "Sin parámetros", "form": ConsultaForm()},
            )

        if not persona:
            return render(
                request,
                "gestion/consulta.html",
                {"error": "Datos incorrectos", "form": ConsultaForm()},
            )

        correo = persona.correo

        # Encontrar Participante/Mentor para el formulario
        if hasattr(persona, "participante"):
            form = RevisarParticipanteForm(instance=Participante.objects.get(correo=correo))
        elif hasattr(persona, "mentor"):
            #! Formulario equivalente para mentores
            form = RevisarParticipanteForm(instance=Mentor.objects.get(correo=correo))
        else:
            messages.error(
                request,
                "La persona encontrada con ese correo no es ni participante ni mentor.",
            )
            return render(request, "vacio.html")

        # Gestionar permisos
        if isinstance(form, RevisarParticipanteForm):
            if not request.user.has_perm("gestion.ver_cv_participante"):
                if "cv" in form.fields:
                    del form.fields["cv"]
            if not request.user.has_perm("gestion.ver_dni_telefono_participante"):
                if "dni" in form.fields:
                    del form.fields["dni"]
                if "telefono" in form.fields:
                    del form.fields["telefono"]

        logger.info(
            f"Mostrando info de participante a {request.user}", extra={"correo": correo}
        )
        return render(request, "verificacion_correcta.html", {"form": form})

    return render(
        request,
        "gestion/consulta.html",
        {"error": "Datos incorrectos", "form": ConsultaForm()},
    )


@require_http_methods(["GET", "POST"])
def normalizacion(request: HttpRequest, campo: str = None):
    if not request.user.has_perm("gestion.change_participante"):
        messages.error(
            request, "No tienes permiso para acceder a la página de normalización."
        )
        return redirect("gestion")

    campos = ("nombre_estudio", "centro_estudio", "curso", "ciudad")

    if not campo or not campo in campos:
        return render(request, "gestion/normalizacion.html", {"campos": campos})

    # order_by necesario (elimina el orden original). Flat da los valores fuera de tuplas.
    valores = Participante.objects.order_by().values_list(campo, flat=True).distinct()

    if request.method == "GET":
        return render(
            request,
            "gestion/normalizacion.html",
            {"form": NormalizacionForm(originales=valores), "campo": campo},
        )

    # POST
    form = NormalizacionForm(request.POST, originales=valores)
    if not form.is_valid():
        return Http404

    data = form.cleaned_data

    if data["originales"] and data["reemplazo"]:
        Participante.objects.filter(**{f"{campo}__in": data["originales"]}).update(
            **{campo: data["reemplazo"]}
        )

    return redirect("normalizacion", campo=campo)
