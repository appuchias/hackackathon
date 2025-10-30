import csv, os

from django.core.management.base import BaseCommand, CommandError

from hackudc.models import Participante


class Command(BaseCommand):
    help = "Crea un archivo CSV con la información de los participantes para su importación en listmonk."

    def add_arguments(self, parser):
        parser.add_argument(
            "archivo", help="Archivo de salida", type="path", default="lista_correo.csv"
        )
        parser.add_argument(
            "--overwrite",
            help="Sobreescribir el archivo de salida si existe.",
            action="store_strue",
            default=False,
        )

    def handle(self, *args, **options):
        if os.path.exists(args.archivo) and not args.overwrite:
            raise CommandError(
                "El archivo de salida existe. Añade --overwrite para sobreescribirlo."
            )

        atributos_extra = ("talla_camiseta",)

        participantes = Participante.objects.filter()
        participantes_info = participantes.values("nombre", "correo", *atributos_extra)

        self.stdout.write(
            self.style.HTTP_INFO(
                f"Encontrados {participantes.count()} participantes. Escribiendo CSV."
            )
        )

        try:
            with open(args.archivo, "w") as csvfile:
                writer = csv.writer(
                    csvfile,
                    delimiter=";",
                    quoting=csv.QUOTE_MINIMAL,
                    fieldnames=("email", "name", "attributes"),
                )

                for participante in participantes_info:
                    nombre = participante.pop("nombre")
                    correo = participante.pop("correo")
                    writer.writerow(nombre, correo, participante)

        except Exception as e:
            e.printStackTrace()
            raise CommandError("Error encontrado mientras se escribía el CSV!")

        self.stdout.write(
            self.style.SUCCESS(
                f"CSV exportado con {participantes.count()} participantes!"
            )
        )
