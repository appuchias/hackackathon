# Copyright (C) 2025-2026  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

import json, logging, os

from django.core.management.base import BaseCommand, CommandError

from gestion.models import Persona, Token

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Exporta la información de las personas en BD para la creación de los passbooks."

    def add_arguments(self, parser):
        parser.add_argument(
            "-o",
            "--output",
            help="Archivo de salida",
            default="personas.json",
        )
        parser.add_argument(
            "--no-overwrite",
            help="Evitar sobreescribir el archivo de salida.",
            action="store_true",
            default=False,
        )

    def handle(self, *args, **options):
        archivo = options.get("output")

        if os.path.exists(archivo) and options.get("no_overwrite"):
            raise CommandError(
                "El archivo de salida existe y se indicó --no-overwrite."
            )

        personas = Persona.objects.filter(
            fecha_aceptacion__isnull=False,
            fecha_confirmacion_plaza__isnull=False,
            fecha_rechazo_plaza__isnull=True
        ).order_by("fecha_registro")

        if not personas.exists():
            self.stdout.write(self.style.ERROR("Ninguna persona a exportar"))
            return

        self.stdout.write(
            self.style.HTTP_INFO(f"Escribiendo {personas.count()} personas.")
        )

        lista_personas = list()

        for persona in personas:
            if hasattr(persona, "participante"):
                tipo = "participante"
            else:
                tipo = "mentor"

            token_confirmacion_plaza = Token.objects.filter(persona=persona, tipo="CONFIRMACION").first()

            lista_personas.append({
                "correo": persona.correo,
                "nombre": persona.nombre,
                "tipo": tipo,
                "token": str(token_confirmacion_plaza.token)
            })

        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(lista_personas, f, ensure_ascii=False)

        logger.info(f"JSON de {personas.count()} personas exportado")

        self.stdout.write(
            self.style.SUCCESS(f"JSON exportado con {personas.count()} personas!")
        )
