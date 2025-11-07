from django.contrib import admin, messages
from django.utils import timezone
from django.utils.translation import ngettext

from gestion.models import (
    Participante,
    Mentor,
    Patrocinador,
    RestriccionAlimentaria,
    Presencia,
    TipoPase,
    Pase,
    Token,
)


def aceptar_participante(modeladmin, request, queryset):
    verificados = queryset.filter(fecha_verificacion_correo__isnull=False)
    no_verificados = queryset.filter(fecha_verificacion_correo__isnull=True)

    ya_aceptados = verificados.filter(fecha_aceptacion__isnull=False).count()
    actualizados = verificados.filter(fecha_aceptacion__isnull=True).update(
        fecha_aceptacion=timezone.now()
    )

    if no_verificados.exists():
        modeladmin.message_user(
            request,
            ngettext(
                "%d participante no tiene el correo verificado y no se ha podido aceptar.",
                "%d participantes no tienen el correo verificado y no se han podido aceptar.",
                no_verificados.count(),
            )
            % no_verificados.count(),
            messages.ERROR,
        )

    if ya_aceptados:
        modeladmin.message_user(
            request,
            ngettext(
                "%d participante ya estaba aceptado.",
                "%d participantes ya estaban aceptados.",
                ya_aceptados,
            )
            % ya_aceptados,
            messages.WARNING,
        )
    if actualizados:
        modeladmin.message_user(
            request,
            ngettext(
                "%d participante aceptado.", "%d participantes aceptados.", actualizados
            )
            % actualizados,
            messages.SUCCESS,
        )
    else:
        modeladmin.message_user(request, "No se ha aceptado a ningún participante.")


class EstadoParticipanteListFilter(admin.SimpleListFilter):
    title = "Estado"
    parameter_name = "estado"

    def lookups(self, request, model_admin):
        return [
            ("registrado", "Registrado (sin verificar correo)"),
            ("verificado", "Correo verificado"),
            ("aceptado", "Aceptado"),
            ("confirmado", "Plaza confirmada"),
        ]

    def queryset(self, request, queryset):
        match self.value():
            case "registrado":
                return queryset.filter(
                    fecha_registro__isnull=False,
                    fecha_verificacion_correo__isnull=True,
                    fecha_aceptacion__isnull=True,
                    fecha_confirmacion_plaza__isnull=True,
                )
            case "verificado":
                return queryset.filter(
                    fecha_registro__isnull=False,
                    fecha_verificacion_correo__isnull=False,
                    fecha_aceptacion__isnull=True,
                    fecha_confirmacion_plaza__isnull=True,
                )
            case "aceptado":
                return queryset.filter(
                    fecha_registro__isnull=False,
                    fecha_verificacion_correo__isnull=False,
                    fecha_aceptacion__isnull=False,
                    fecha_confirmacion_plaza__isnull=True,
                )
            case "confirmado":
                return queryset.filter(
                    fecha_registro__isnull=False,
                    fecha_verificacion_correo__isnull=False,
                    fecha_aceptacion__isnull=False,
                    fecha_confirmacion_plaza__isnull=False,
                )


class TokenValidoListFilter(admin.SimpleListFilter):
    title = "Validez"
    parameter_name = "validez"

    def lookups(self, request, model_admin):
        return [
            ("valido", "Válido"),
            ("expirado", "Expirado"),
        ]

    def queryset(self, request, queryset):
        match self.value():
            case "valido":
                return queryset.filter(fecha_expiracion__gte=timezone.now())
            case "expirado":
                return queryset.filter(fecha_expiracion__lt=timezone.now())


class ParticipanteAdmin(admin.ModelAdmin):
    list_display = [
        "correo",
        "nombre",
        "nombre_estudio",
        "centro_estudio",
        "ciudad",
        "quiere_creditos",
        "fecha_registro",
        "verificado",
        "aceptado",
        "confirmado",
    ]
    list_filter = [EstadoParticipanteListFilter, "centro_estudio", "ciudad"]
    actions = [aceptar_participante]


class TokenAdmin(admin.ModelAdmin):
    fields = [
        "token",
        "tipo",
        "persona",
        "fecha_creacion",
        "fecha_expiracion",
        "fecha_uso",
    ]
    readonly_fields = [
        "token",
        "fecha_creacion",
    ]

    radio_fields = {"tipo": admin.HORIZONTAL}

    list_display = [
        "persona",
        "tipo",
        "fecha_creacion",
        "valido",
    ]
    list_filter = [
        "tipo",
        TokenValidoListFilter,
    ]

    search_fields = [
        "persona",
    ]


# Register your models here.
admin.site.register(Patrocinador)
admin.site.register(Mentor)
admin.site.register(Participante, ParticipanteAdmin)
admin.site.register(RestriccionAlimentaria)
admin.site.register(Presencia)
admin.site.register(TipoPase)
admin.site.register(Pase)
admin.site.register(Token, TokenAdmin)
