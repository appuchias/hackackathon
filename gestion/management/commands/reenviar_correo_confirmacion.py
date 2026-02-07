# Copyright (C) 2025-2026  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

from datetime import datetime, timedelta
import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from gestion.models import Persona
from gestion.utils import enviar_correo_confirmacion

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Reenvía el correo de confirmación a la persona con el correo indicado"

    def add_arguments(self, parser):
        parser.add_argument("correo", help="Correo de la Persona")
        # grupo_fecha_expiracion = parser.add_mutually_exclusive_group()
        # grupo_fecha_expiracion.add_argument(
        #     "-d",
        #     "--dias",
        #     help="Días de duración del token. (default=14)",
        #     type=int,
        #     default=14,
        # )
        # grupo_fecha_expiracion.add_argument(
        #     "-e",
        #     "--expiracion",
        #     help="Fecha de expiración para todos los tokens. Formato ISO 8601.",
        # )

    def handle(self, *args, **options):
        correo = options.get("correo")

        persona = Persona.objects.get(correo=correo)

        # dias = options.get("dias")
        # expiracion = options.get("expiracion")
        # if expiracion:
        #     fecha_expiracion = datetime.fromisoformat(expiracion).astimezone(
        #         timezone.get_current_timezone()
        #     )
        # else:
        #     fecha_expiracion = (timezone.now() + timedelta(days=dias)).astimezone(
        #         timezone.get_current_timezone()
        #     ).replace(
        #         hour=23, minute=59, second=59
        #     )
        #
        # if fecha_expiracion < timezone.now():
        #     raise ValueError("La fecha de expiración es anterior a este instante")

        estado = enviar_correo_confirmacion(persona)
        if estado != 0:
            self.stdout.write(
                self.style.ERROR(
                    f"Error al enviar el correo de confirmación ({correo})."
                )
            )

        self.stdout.write(
            self.style.SUCCESS("Correo de confirmación reenviado correctamente.")
        )
