# Copyright (C) 2025-2026  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

import csv, logging, os, shutil

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from gestion.models import Participante

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Exporta la información de los participantes en CSV para su revisión."

    def add_arguments(self, parser):
        parser.add_argument(
            "-o",
            "--output",
            help="Ruta de salida",
            default="cvs",
        )
        parser.add_argument(
            "--all",
            help="Exportar todos los participantes. Por defecto solo se exportan los que asistieron al evento.",
            action="store_true",
            default=False,
        )

    def handle(self, *args, **options):
        ruta_salida = options.get("output", "")

        if not os.path.exists(ruta_salida):
            os.makedirs(ruta_salida)

        if not ruta_salida[-1] == "/":
            ruta_salida = ruta_salida + "/"

        participantes = Participante.objects.filter(quiere_creditos=True)
        if not options.get("all"):
            participantes = participantes.filter(acreditacion__isnull=False)

        if not participantes.exists():
            self.stdout.write(self.style.ERROR("Ningún CV que exportar"))
            return

        self.stdout.write(
            self.style.HTTP_INFO(f"Copiando {participantes.count()} CVs.")
        )

        for participante in participantes:
            try:
                src = participante.cv.path
                dst = (
                    ruta_salida
                    + participante.correo.replace("@", "-").replace(".", "-")
                    + ".pdf"
                )
                shutil.copy2(src, dst)
            except ValueError:
                self.stdout.write(
                    self.style.ERROR(
                        f"El participante {participante.correo} no tiene CV!"
                    )
                )

        self.stdout.write(self.style.SUCCESS(f"CVs exportados!"))
