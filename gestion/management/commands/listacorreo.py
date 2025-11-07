import csv, os

from django.core.management.base import BaseCommand, CommandError

from gestion.models import Participante


# email,name,attributes
# user1@mail.com,"User One","{""age"": 42, ""planet"": ""Mars""}"
# user2@mail.com,"User Two","{""age"": 24, ""job"": ""Time Traveller""}"


class Command(BaseCommand):
    help = "Exporta la información de los participantes en CSV para su importación en listmonk."

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

    def handle(self, *args, **options):
        archivo = options.get("output")

        if os.path.exists(archivo) and options.get("no_overwrite"):
            raise CommandError(
                "El archivo de salida existe y se indicó --no-overwrite."
            )

        atributos_extra = ("talla_camiseta",)

        participantes = Participante.objects.filter()
        participantes_info = participantes.values("correo", "nombre", *atributos_extra)

        self.stdout.write(
            self.style.HTTP_INFO(
                f"Encontrados {participantes.count()} participantes. Escribiendo CSV."
            )
        )

        try:
            with open(archivo, "w") as csvfile:
                writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL, quotechar='"')
                writer.writerow(("email", "name", "attributes"))

                for participante in participantes_info:
                    correo = participante.pop("correo")
                    nombre = participante.pop("nombre")
                    atributos = str(participante).replace("'", '"')

                    writer.writerow((correo, nombre, atributos))

        except Exception as e:
            self.stdout.write(
                self.style.ERROR("Error encontrado mientras se escribía el CSV!")
            )
            raise e

        self.stdout.write(
            self.style.SUCCESS(
                f"CSV exportado con {participantes.count()} participantes!"
            )
        )
