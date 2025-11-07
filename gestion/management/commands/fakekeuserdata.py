# Copyright (C) 2025-now  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

from random import choice, randint

from django.core.management.base import BaseCommand, CommandError
from faker import Faker

from gestion.models import Participante


class Command(BaseCommand):
    help = "Crea datos falsos de participantes de prueba"

    def add_arguments(self, parser):
        parser.add_argument(
            "cantidad", help="Cantidad de participantes a crear", type=int, default=100
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(f"Se crearán {options['cantidad']} participantes")
        )
        fake = Faker("es_ES")

        for _ in range(options["cantidad"]):
            participante = Participante(
                correo=fake.email(),
                nombre=fake.name(),
                dni=fake.cif(),  # Lo más parecido a un DNI que hay en faker...
                genero=choice(["Hombre", "Mujer", "Otro"]),
                telefono=fake.phone_number(),
                ano_nacimiento=fake.year(),
                nombre_estudio=choice(["GCED", "GEI", "MUEI", "MUNICS"]),
                centro_estudio=choice(["FIC", "USC", "UVigo", "Otro"]),
                curso=randint(1, 4),
                ciudad=fake.city(),
                quiere_creditos=choice([True, False]),
                talla_camiseta=choice(["S", "M", "L", "XL"]),
                compartir_cv=choice([True, False]),
            )

            Participante.save(participante)
