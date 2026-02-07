# Copyright (C) 2025-2026  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from gestion.models import Colaborador, Persona, Token

logger = logging.getLogger(__name__)


def enviar_correo_verificacion(
    persona: Persona, fecha_expiracion: datetime | None = None
) -> int:
    """
    Envía la verificación de correo a la Persona indicada.
    Si la Persona tiene un token válido lo reutiliza, modificando la fecha de expiración.
    En caso contrario, crea uno nuevo.

    Argumentos:
        persona: `Persona` a la que enviar el correo.
        fecha_expiracion: Fecha de expiración del token de confirmación (Opcional).

    Salida:
        0: Envío correcto.
        1: Error en el envío.
    """

    token = Token.objects.filter(
        persona=persona, tipo="VERIFICACION", fecha_uso__isnull=True
    ).first()
    if not token:
        token = Token(persona=persona, tipo="VERIFICACION")

    if not fecha_expiracion:
        fecha_expiracion = (
            (timezone.now() + timedelta(days=7))
            .astimezone(timezone.get_default_timezone())
            .replace(hour=23, minute=59, second=59)
        )

    token.fecha_expiracion = fecha_expiracion
    token.save()

    params = {
        "nombre": persona.nombre,
        "token": token.token,
        "host": settings.HOST_REGISTRO,
    }

    try:
        send_mail(
            subject=settings.EMAIL_VERIFICACION_ASUNTO,
            message=render_to_string("correo/verificacion_correo.txt", params),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=(persona.correo,),
            html_message=render_to_string("correo/verificacion_correo.html", params),
            fail_silently=False,
        )

    except Exception as e:
        persona.motivo_error_correo_verificacion = str(e)[:4096]
        persona.save()

        logger.error("Error al enviar el correo de verificación:")
        logger.error(e, stack_info=True, extra={"correo": persona.correo})

        return 1

    logger.info("Correo de verificación enviado", extra={"correo": persona.correo})
    return 0


def enviar_correo_verificacion_correcta(persona: Persona) -> int:
    """
    Envía el correo de verificación correcta a la Persona indicada.

    Argumentos:
        persona: `Persona` a la que enviar el correo.

    Salida:
        0: Envío correcto.
        1: Error en el envío.
    """
    token = Token.objects.get(persona=persona, tipo="VERIFICACION")

    params = {
        "nombre": persona.nombre,
        "token": token.token,
        "host": settings.HOST_REGISTRO,
    }

    try:
        send_mail(
            subject=settings.EMAIL_VERIFICACION_CORRECTA_ASUNTO,
            message=render_to_string("correo/verificacion_correo_correcta.txt", params),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=(persona.correo,),
            html_message=render_to_string(
                "correo/verificacion_correo_correcta.html", params
            ),
            fail_silently=False,
        )
    except ConnectionRefusedError as e:
        logger.error(f"Error en el envío del correo de verificación correcta:")
        logger.error(e, stack_info=True, extra={"correo": persona.correo})

        return 1

    logger.info("Correo de confirmación enviado", extra={"correo": persona.correo})
    return 0


def enviar_correo_confirmacion(
    persona: Persona, fecha_expiracion: datetime | None = None
) -> int:
    """
    Envía la confirmación de plaza a la Persona indicada.
    Si la Persona tiene un token válido lo reutiliza, modificando la fecha de expiración.
    En caso contrario, crea uno nuevo.

    Argumentos:
        persona: `Persona` a la que enviar el correo.
        fecha_expiracion: Fecha de expiración del token de confirmación (Opcional).

    Salida:
        0: Envío correcto.
        1: Error en el envío.
    """
    token = Token.objects.filter(
        persona=persona, tipo="CONFIRMACION", fecha_uso__isnull=True
    ).first()
    if not token:
        token = Token(persona=persona, tipo="CONFIRMACION")

    if not fecha_expiracion:
        fecha_expiracion = (
            (timezone.now() + timedelta(days=14))
            .astimezone(timezone.get_default_timezone())
            .replace(hour=23, minute=59, second=59)
        )

    token.fecha_expiracion = fecha_expiracion
    token.save()

    params = {
        "nombre": persona.nombre,
        "token": token.token,
        "expiracion": fecha_expiracion,
        "host": settings.HOST_REGISTRO,
    }

    try:
        send_mail(
            subject=settings.EMAIL_CONFIRMACION_ASUNTO,
            message=render_to_string("correo/confirmacion_plaza.txt", params),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=(persona.correo,),
            html_message=render_to_string("correo/confirmacion_plaza.html", params),
            fail_silently=False,
        )
    except ConnectionRefusedError as e:
        logger.error(f"Error en el envío del correo de confirmación:")
        logger.error(e, stack_info=True, extra={"correo": persona.correo})

        return 1

    logger.info("Correo de confirmación enviado", extra={"correo": persona.correo})
    return 0


def enviar_correo_aceptacion_plaza(persona: Persona) -> int:
    """
    Envía la aceptación de plaza a la Persona indicada.

    Argumentos:
        persona: `Persona` a la que enviar el correo.

    Salida:
        0: Envío correcto.
        1: Error en el envío.
    """
    token_verificacion = Token.objects.get(persona=persona, tipo="VERIFICACION")
    token_confirmacion = Token.objects.get(persona=persona, tipo="CONFIRMACION")

    params = {
        "nombre": persona.nombre,
        "host": settings.HOST_REGISTRO,
        "token_verificacion": token_verificacion,
        "token_confirmacion": token_confirmacion,
    }

    try:
        send_mail(
            subject=settings.EMAIL_ACEPTACION_ASUNTO,
            message=render_to_string("correo/aceptacion_plaza.txt", params),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=(persona.correo,),
            html_message=render_to_string("correo/aceptacion_plaza.html", params),
            fail_silently=False,
        )
    except ConnectionRefusedError as e:
        logger.error(f"Error en el envío del correo de aceptación:")
        logger.error(e, stack_info=True, extra={"correo": persona.correo})

        return 1

    logger.info("Correo de aceptación enviado", extra={"correo": persona.correo})
    return 0


def enviar_correo_rechazo_plaza(persona: Persona) -> int:
    """
    Envía el rechazo de plaza a la Persona indicada.

    Argumentos:
        persona: `Persona` a la que enviar el correo.

    Salida:
        0: Envío correcto.
        1: Error en el envío.
    """
    params = {
        "nombre": persona.nombre,
        "host": settings.HOST_REGISTRO,
    }

    try:
        send_mail(
            subject=settings.EMAIL_RECHAZO_ASUNTO,
            message=render_to_string("correo/rechazo_plaza.txt", params),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=(persona.correo,),
            html_message=render_to_string("correo/rechazo_plaza.html", params),
            fail_silently=False,
        )
    except ConnectionRefusedError as e:
        logger.error(f"Error en el envío del correo de rechazo:")
        logger.error(e, stack_info=True, extra={"correo": persona.correo})

        return 1

    logger.info("Correo de rechazo enviado", extra={"correo": persona.correo})
    return 0


def enviar_correo_colaborador(colaborador: Colaborador) -> int:
    """
    Envía el correo de confirmación de solicitud recibida al colaborador correspondiente

    Argumentos:
        colaborador: `Colaborador` al que enviar el correo.

    Salida:
        0: Envío correcto.
        1: Error en el envío.
    """
    params = {
        "nombre": colaborador.nombre,
        "host": settings.HOST_REGISTRO,
    }

    try:
        send_mail(
            subject=settings.EMAIL_COLABORADOR_ASUNTO,
            message=render_to_string("correo/solicitud_colaborador.txt", params),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=(colaborador.correo,),
            html_message=render_to_string("correo/solicitud_colaborador.html", params),
            fail_silently=False,
        )
    except ConnectionRefusedError as e:
        logger.error(f"Error en el envío del correo de colaborador:")
        logger.error(e, stack_info=True, extra={"correo": colaborador.correo})

        return 1

    logger.info("Correo de colaborador enviado", extra={"correo": colaborador.correo})
    return 0
