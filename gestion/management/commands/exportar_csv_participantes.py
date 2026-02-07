# Copyright (C) 2025-2026  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

import csv, logging, os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from gestion.models import Participante

logger = logging.getLogger(__name__)


# Formato de salida:
# correo,nombre,<atributo1>,<atributo2>,...
# user1@mail.com,"User One",atr1,atr2,...
# user2@mail.com,"User Two",atr1,atr2,...


class Command(BaseCommand):
    help = "Exporta la información de los participantes en CSV para su revisión."

    def add_arguments(self, parser):
        parser.add_argument(
            "-o",
            "--output",
            help="Archivo de salida",
            default="lista_correo.csv",
        )
        parser.add_argument(
            "--no-overwrite",
            help="Evitar sobreescribir el archivo de salida.",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "--all",
            help="Exportar todos los participantes. Por defecto solo se exportan los que verificaron el correo.",
            action="store_true",
            default=False,
        )

    def handle(self, *args, **options):
        archivo = options.get("output")

        if os.path.exists(archivo) and options.get("no_overwrite"):
            raise CommandError(
                "El archivo de salida existe y se indicó --no-overwrite."
            )

        atributos = (
            "correo",
            "nombre",
            "fecha_registro",
            "ciudad",
            "nivel_estudio",
            "centro_estudio",
            "nombre_estudio",
            "curso",
            "quiere_creditos",
            "motivacion",
            "cv",
        )

        if options.get("all"):
            participantes = Participante.objects.all()
        else:
            participantes = Participante.objects.filter(
                fecha_verificacion_correo__isnull=False
            )

        if not participantes.exists():
            self.stdout.write(
                self.style.ERROR("Ningún participante tiene el correo verificado")
            )
            return

        self.stdout.write(
            self.style.HTTP_INFO(f"Escribiendo {participantes.count()} participantes.")
        )

        participantes_info = participantes.order_by("fecha_registro").values(*atributos)

        try:
            with open(archivo, "w") as csvfile:
                writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL, quotechar='"')
                writer.writerow((*atributos,))

                for participante in participantes_info:
                    participante["cv"] = (
                        f"https://{settings.HOST_REGISTRO}{settings.MEDIA_URL}{participante["cv"]}"
                    )

                    writer.writerow((*participante.values(),))

        except Exception as e:
            self.stdout.write(
                self.style.ERROR("Error encontrado mientras se escribía el CSV!")
            )
            raise e

        logger.info(f"CSV de {participantes.count()} participantes exportado")

        self.stdout.write(
            self.style.SUCCESS(
                f"CSV exportado con {participantes.count()} participantes!"
            )
        )
