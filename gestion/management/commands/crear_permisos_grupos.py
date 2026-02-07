# Copyright (C) 2025-2026  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Crea los grupos base para la gestión de usuarios y asigna permisos"

    def handle(self, *args, **options):

        # modelos_disponibles = [
        #     "colaborador",
        #     "mentor",
        #     "participante",
        #     "pase",
        #     "persona",
        #     "presencia",
        #     "restriccionalimentaria",
        #     "tipopase",
        #     "token",
        # ]

        # Grupos
        permisos = {
            "Administradores": self.obtener_permisos(
                ["participante", "mentor", "tipopase"], view=True, add=True, change=True
            )
            + [
                "aceptar_participante",
                "ver_cv_participante",
                "ver_dni_telefono_participante",
            ],
            "Revisores": self.obtener_permisos(["participante"], view=True)
            + [
                "aceptar_participante",
                "ver_cv_participante",
            ],
            "Ver modelos de gestión": self.obtener_permisos(
                ["participante"], view=True
            ),
        }

        for nombre, permisos_grupo in permisos.items():
            grupo, _creado = Group.objects.get_or_create(name=nombre)
            grupo.permissions.set(
                (
                    Permission.objects.filter(codename=f"add_{permiso}").first()
                    for permiso in permisos_grupo
                )
            )

            if _creado:
                self.stdout.write(self.style.SUCCESS(f"Grupo '{nombre}' creado"))
            self.stdout.write(self.style.SUCCESS(f"Permisos asignados a '{nombre}'"))

    # Permisos genéricos para los modelos relevantes
    def obtener_permisos(
        self, modelos, add=False, change=False, delete=False, view=False
    ):
        permisos = list()

        if add:
            permisos.extend([f"add_{m}" for m in modelos])
        if change:
            permisos.extend([f"change_{m}" for m in modelos])
        if delete:
            permisos.extend([f"delete_{m}" for m in modelos])
        if view:
            permisos.extend([f"view_{m}" for m in modelos])

        return permisos
