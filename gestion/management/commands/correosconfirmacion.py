# Copyright (C) 2025-2026  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

import logging, time
from datetime import datetime, timedelta
from itertools import batched

from django.conf import settings
from django.core.management import BaseCommand
from django.utils import timezone

from gestion.models import Participante, Token
from gestion.utils import enviar_correo_confirmacion

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Envía un correo de confirmación a los participantes aceptados no confirmados"
    )

    def add_arguments(self, parser):
        grupo_fecha_expiracion = parser.add_mutually_exclusive_group()
        grupo_fecha_expiracion.add_argument(
            "-d",
            "--dias",
            help="Días de duración del token. (default=14)",
            type=int,
            default=14,
        )
        grupo_fecha_expiracion.add_argument(
            "-e",
            "--expiracion",
            help="Fecha de expiración para todos los tokens. Formato ISO 8601.",
        )

    def handle(self, *args, **options):
        dias = options.get("dias")
        expiracion = options.get("expiracion")
        if expiracion:
            fecha_expiracion = datetime.fromisoformat(expiracion).astimezone(
                timezone.get_current_timezone()
            )
        else:
            fecha_expiracion = (
                (timezone.now() + timedelta(days=dias))
                .astimezone(timezone.get_current_timezone())
                .replace(hour=23, minute=59, second=59)
            )

        if fecha_expiracion < timezone.now():
            raise ValueError("La fecha de expiración es anterior a este instante")

        # Participantes aceptados pero sin confirmar la plaza
        participantes = Participante.objects.filter(
            fecha_aceptacion__isnull=False,
            fecha_confirmacion_plaza__isnull=True,
            fecha_rechazo_plaza__isnull=True,
        ).order_by("fecha_registro")

        participantes_con_token = Token.objects.filter(
            tipo="CONFIRMACION", persona__in=participantes
        )
        if participantes_con_token.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"{participantes_con_token.count()} participantes ya tenían un token de confirmación"
                )
            )

            # No enviar correo de confirmación a los usuarios a los que ya se les haya enviado
            participantes = participantes.exclude(
                correo__in=participantes_con_token.values("persona_id")
            )

        self.stdout.write(
            f"Enviando {participantes.count()} correos de confirmación.",
            self.style.HTTP_INFO,
        )

        c = input("¿Continuar? [S/n] ")
        if c.lower() != "s" and c != "":
            return


        errores_permitidos = 5
        inicio_batch = 0

        for batch in batched(participantes, settings.EMAIL_MESSAGE_RATE):
            if errores_permitidos <= 0:
                break

            # Evitar mandar más del límite de mensajes
            if time.perf_counter() - inicio_batch < 1:
                # Añadir 100ms de margen
                time.sleep(1 - (time.perf_counter() - inicio_batch) + 0.1)

            inicio_batch = time.perf_counter()

            for participante in batch:
                estado = enviar_correo_confirmacion(participante, fecha_expiracion)
                if estado != 0:
                    # Token.objects.get(persona=participante).delete()
                    errores_permitidos -= 1
                    logger.error(f"Error al mandar el correo a {participante.correo}")
                    self.stdout.write(
                        self.style.ERROR(
                            f"Error al mandar el correo a {participante.correo}"
                        )
                    )
                    break

                self.stdout.write(
                    self.style.HTTP_INFO(f"Mensaje enviado a {participante.correo}")
                )
        else:
            logger.info("Todos los correos de confirmación enviados correctamente")
            self.stdout.write(
                self.style.SUCCESS(
                    "Todos los correos de confirmación enviados correctamente"
                )
            )
