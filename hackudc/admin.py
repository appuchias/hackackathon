from django.contrib import admin

from hackudc.models import *


def aceptar_participante(modeladmin, request, queryset):
    queryset.update(aceptado=True)


class ParticipanteAdmin(admin.ModelAdmin):
    list_display = [
        "correo",
        "nombre",
        "nombre_estudio",
        "centro_estudio",
        "ciudad",
        "quiere_creditos",
        "aceptado",
    ]
    list_filter = ["aceptado", "centro_estudio", "ciudad"]
    actions = [aceptar_participante]


# Register your models here.
admin.site.register(Patrocinador)
admin.site.register(Mentor)
admin.site.register(Participante, ParticipanteAdmin)
admin.site.register(RestriccionAlimentaria)
admin.site.register(Presencia)
admin.site.register(TipoPase)
admin.site.register(Pase)
