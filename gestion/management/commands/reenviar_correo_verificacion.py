# Copyright (C) 2025-2026  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

import logging

from django.core.management.base import BaseCommand

from gestion.models import Persona
from gestion.utils import enviar_correo_verificacion

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Reenvía el correo de verificación a la persona con el correo indicado"

    def add_arguments(self, parser):
        parser.add_argument("correo", help="Correo de la Persona")

    def handle(self, *args, **options):
        correo = options.get("correo")

        persona = Persona.objects.get(correo=correo)

        estado = enviar_correo_verificacion(persona)
        if estado != 0:
            self.stdout.write(
                self.style.ERROR(
                    f"Error al enviar el correo de verificación ({correo})."
                )
            )

        self.stdout.write(
            self.style.SUCCESS("Correo de verificación reenviado correctamente.")
        )
