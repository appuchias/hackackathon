# Copyright (C) 2025-now  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

import logging
from django.core.management import BaseCommand, CommandError
from django.core.validators import validate_email

from gestion.models import Persona, Participante, Mentor, Token


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Cambia el correo del participante seleccionado."

    def add_arguments(self, parser):
        parser.add_argument("original", help="Correo de la persona a modificar")
        parser.add_argument("nuevo", help="Correo modificado")

    def handle(self, *args, **options):
        original, nuevo = options.get("original"), options.get("nuevo")

        validate_email(original)
        validate_email(nuevo)

        persona = Persona.objects.get(correo=original)

        try:
            subclase = persona.participante
        except Participante.DoesNotExist:
            try:
                subclase = persona.mentor
            except Mentor.DoesNotExist:
                subclase = None
        if not subclase:
            raise CommandError("La persona no es ni participante ni mentor.")

        # Actualizar correo de la persona y el participante/mentor
        persona.correo = nuevo
        persona.dni += " "
        subclase.correo = nuevo
        subclase.dni += " "
        persona.save()
        subclase.save()

        # Actualizar tokens asociados
        Token.objects.filter(persona=Persona.objects.get(correo=original)).update(
            persona=persona
        )

        # Eliminar la persona antigua
        Persona.objects.get(correo=original).delete()

        # Corregir los DNIs
        persona.dni = persona.dni.strip()
        subclase.dni = subclase.dni.strip()
        persona.save()
        subclase.save()

        logger.info(f"Correo de {original} modificado a {nuevo}")
        self.stdout.write(
            self.style.SUCCESS(f"Correo de {original} modificado a {nuevo}")
        )
