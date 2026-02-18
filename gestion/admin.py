# Copyright (C) 2025-2026  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>
import datetime, logging
from datetime import timedelta

from django.contrib import admin, messages
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ngettext

from gestion.models import (
    Empresa,
    Mentor,
    Participante,
    Pase,
    Colaborador,
    Presencia,
    RestriccionAlimentaria,
    TipoPase,
    Token,
)
from gestion.utils import enviar_correo_confirmacion, enviar_correo_verificacion

logger = logging.getLogger(__name__)


@admin.action(
    permissions=["reenviar_verificacion"],
    description="Reenviar la verificación de correo",
)
def reenviar_correo_verificacion(modeladmin, request, queryset):
    if not request.user.has_perm("gestion.reenviar_verificacion"):
        modeladmin.message_user(
            request, "No tienes permiso para realizar esta acción", messages.ERROR
        )
        return

    if queryset.count() > 1:
        modeladmin.message_user(
            request,
            "Solo puedes reenviar el correo de verificación a un participante de cada vez.",
            messages.ERROR,
        )
        return

    estado = enviar_correo_verificacion(queryset.first())
    if estado != 0:
        modeladmin.message_user(
            request,
            f"Error al enviar el correo de verificación ({queryset.first().correo}).",
            messages.ERROR,
        )
        return

    modeladmin.message_user(
        request,
        "Correo de verificación reenviado correctamente.",
        messages.SUCCESS,
    )


@admin.action(
    permissions=["reenviar_confirmacion"],
    description="Reenviar la confirmación de plaza",
)
def reenviar_correo_confirmacion(modeladmin, request, queryset):
    if not request.user.has_perm("gestion.reenviar_confirmacion"):
        modeladmin.message_user(
            request, "No tienes permiso para realizar esta acción", messages.ERROR
        )
        return

    if queryset.count() > 1:
        modeladmin.message_user(
            request,
            "Solo puedes reenviar el correo de confirmación a un participante de cada vez.",
            messages.ERROR,
        )
        return

    estado = enviar_correo_confirmacion(queryset.first())
    if estado != 0:
        modeladmin.message_user(
            request,
            f"Error al enviar el correo de confirmación ({queryset.first().correo}).",
            messages.ERROR,
        )
        return

    modeladmin.message_user(
        request,
        "Correo de confirmación reenviado correctamente.",
        messages.SUCCESS,
    )


@admin.action(permissions=["aceptar"], description="Aceptar persona(s)")
def aceptar_personas(modeladmin, request, queryset):
    if not request.user.has_perm("gestion.aceptar_participante"):
        modeladmin.message_user(
            request, "No tienes permiso para realizar esta acción", messages.ERROR
        )
        return

    verificados = queryset.filter(fecha_verificacion_correo__isnull=False)
    no_verificados = queryset.filter(fecha_verificacion_correo__isnull=True)

    ya_aceptados = verificados.filter(fecha_aceptacion__isnull=False).count()
    actualizados = verificados.filter(fecha_aceptacion__isnull=True).update(
        fecha_aceptacion=timezone.now()
    )

    logger.info(
        f"Acción 'aceptar_personas' ejecutada por {request.user.username}: {actualizados} aceptados. {no_verificados.count()} no verificados. {ya_aceptados} ya aceptados"
    )

    if no_verificados.exists():
        modeladmin.message_user(
            request,
            ngettext(
                "%d persona no tiene el correo verificado y no se ha podido aceptar.",
                "%d personas no tienen el correo verificado y no se han podido aceptar.",
                no_verificados.count(),
            )
            % no_verificados.count(),
            messages.ERROR,
        )

    if ya_aceptados:
        modeladmin.message_user(
            request,
            ngettext(
                "%d persona ya estaba aceptada.",
                "%d personas ya estaban aceptadas.",
                ya_aceptados,
            )
            % ya_aceptados,
            messages.WARNING,
        )
    if actualizados:
        modeladmin.message_user(
            request,
            ngettext("%d persona aceptada.", "%d personas aceptadas.", actualizados)
            % actualizados,
            messages.SUCCESS,
        )
    else:
        modeladmin.message_user(request, "No se ha aceptado a ninguna persona.")


class EstadoPersonaListFilter(admin.SimpleListFilter):
    title = "Estado"
    parameter_name = "estado"

    def lookups(self, request, model_admin):
        return [
            ("registrado", "Registrado (sin verificar correo)"),
            ("error_verificacion", "Error de verificación del correo"),
            ("verificado", "Correo verificado"),
            ("aceptado", "Aceptado"),
            ("confirmado", "Plaza confirmada"),
            ("rechazo", "Plaza rechazada"),
        ]

    def queryset(self, request, queryset):
        match self.value():
            case "registrado":
                return queryset.filter(
                    fecha_registro__isnull=False,
                    motivo_error_correo_verificacion__isnull=True,
                    fecha_verificacion_correo__isnull=True,
                    fecha_aceptacion__isnull=True,
                    fecha_confirmacion_plaza__isnull=True,
                    fecha_rechazo_plaza__isnull=True,
                )
            case "error_verificacion":
                return queryset.filter(
                    fecha_registro__isnull=False,
                    motivo_error_correo_verificacion__isnull=False,
                    fecha_verificacion_correo__isnull=True,
                    fecha_aceptacion__isnull=True,
                    fecha_confirmacion_plaza__isnull=True,
                    fecha_rechazo_plaza__isnull=True,
                )
            case "verificado":
                return queryset.filter(
                    fecha_registro__isnull=False,
                    fecha_verificacion_correo__isnull=False,
                    fecha_aceptacion__isnull=True,
                    fecha_confirmacion_plaza__isnull=True,
                    fecha_rechazo_plaza__isnull=True,
                )
            case "aceptado":
                return queryset.filter(
                    fecha_registro__isnull=False,
                    fecha_verificacion_correo__isnull=False,
                    fecha_aceptacion__isnull=False,
                    fecha_confirmacion_plaza__isnull=True,
                    fecha_rechazo_plaza__isnull=True,
                )
            case "confirmado":
                return queryset.filter(
                    fecha_registro__isnull=False,
                    fecha_verificacion_correo__isnull=False,
                    fecha_aceptacion__isnull=False,
                    fecha_confirmacion_plaza__isnull=False,
                    fecha_rechazo_plaza__isnull=True,
                )
            case "rechazo":
                return queryset.filter(
                    fecha_registro__isnull=False,
                    fecha_verificacion_correo__isnull=False,
                    fecha_aceptacion__isnull=False,
                    fecha_rechazo_plaza__isnull=False,
                )


class TokenValidoListFilter(admin.SimpleListFilter):
    title = "validez"
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


class TokenUsadoListFilter(admin.SimpleListFilter):
    title = "uso"
    parameter_name = "uso"

    def lookups(self, request, model_admin):
        return [
            ("usado", "Usado"),
            ("no_usado", "No usado"),
        ]

    def queryset(self, request, queryset):
        match self.value():
            case "usado":
                return queryset.filter(fecha_uso__isnull=False)
            case "no_usado":
                return queryset.filter(fecha_uso__isnull=True)


class TokenInline(admin.TabularInline):
    model = Token
    show_change_link = True
    can_delete = False
    max_num = 4
    extra = 0

    fields = [
        "tipo",
        "fecha_creacion",
        "fecha_expiracion",
        "fecha_uso",
    ]

    readonly_fields = [
        "tipo",
        "fecha_creacion",
        "fecha_expiracion",
        "fecha_uso",
    ]


class ParticipanteAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            "Personal",
            {
                "fields": [
                    "nombre",
                    "correo",
                    "genero",
                    "fecha_nacimiento",
                    "ciudad",
                    # "telefono",
                    # "dni",
                    # "cv",
                    "compartir_cv",
                ]
            },
        ),
        (
            "Estudios",
            {
                "fields": [
                    "nivel_estudio",
                    "nombre_estudio",
                    "centro_estudio",
                    "curso",
                    "quiere_creditos",
                ]
            },
        ),
        (
            "Evento",
            {
                "fields": [
                    "acreditacion",
                    "restricciones_alimentarias",
                    "detalle_restricciones_alimentarias",
                    "talla_camiseta",
                    "fecha_registro",
                    "fecha_verificacion_correo",
                    "fecha_aceptacion",
                    "fecha_confirmacion_plaza",
                    "fecha_rechazo_plaza",
                    "motivo_error_correo_verificacion",
                    "motivacion",
                    "notas",
                ]
            },
        ),
    ]

    readonly_fields = [
        "cv",
        "fecha_registro",
        "fecha_verificacion_correo",
        "fecha_aceptacion",
        "fecha_confirmacion_plaza",
        "fecha_rechazo_plaza",
        "motivo_error_correo_verificacion",
    ]

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
        "rechazo",
        "error_verificacion",
    ]
    list_filter = [
        EstadoPersonaListFilter,
        "nivel_estudio",
        "centro_estudio",
        "nombre_estudio",
        "ciudad",
    ]

    search_fields = [
        "correo",
        "nombre",
    ]

    actions = [
        aceptar_personas,
        reenviar_correo_verificacion,
        reenviar_correo_confirmacion,
    ]

    inlines = [
        TokenInline,
    ]

    def change_view(self, request, object_id, form_url="", extra_context=None):
        personal_fields = self.fieldsets[0][1]["fields"]

        # Permiso para ver el CV
        if request.user.has_perm("gestion.ver_cv_participante"):
            if "cv" not in personal_fields:
                personal_fields.insert(5, "cv")
        if not request.user.has_perm("gestion.ver_cv_participante"):
            if "cv" in personal_fields:
                personal_fields.remove("cv")
                logger.debug(f"{request.user.username} no tiene permiso para ver CVs.")

        # Permiso para ver DNI y teléfono
        if request.user.has_perm("gestion.ver_dni_telefono_participante"):
            if "dni" not in personal_fields:
                personal_fields.insert(5, "dni")
            if "telefono" not in personal_fields:
                personal_fields.insert(5, "telefono")
        if not request.user.has_perm("gestion.ver_dni_telefono_participante"):
            if "dni" in personal_fields:
                personal_fields.remove("dni")
                logger.debug(f"{request.user.username} no tiene permiso para ver DNIs.")

            if "telefono" in personal_fields:
                personal_fields.remove("telefono")
                logger.debug(
                    f"{request.user.username} no tiene permiso para ver teléfonos."
                )

        return super(ParticipanteAdmin, self).change_view(
            request, object_id, form_url, extra_context
        )

    def has_aceptar_permission(self, request):
        return request.user.has_perm("gestion.aceptar_participante")

    def has_reenviar_verificacion_permission(self, request):
        return request.user.has_perm("gestion.reenviar_verificacion")

    def has_reenviar_confirmacion_permission(self, request):
        return request.user.has_perm("gestion.reenviar_confirmacion")


class MentorAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            "Personal",
            {
                "fields": [
                    "nombre",
                    "correo",
                    "genero",
                    "fecha_nacimiento",
                    "ciudad",
                    # "telefono",
                    # "dni",
                    # "cv",
                    "compartir_cv",
                ]
            },
        ),
        (
            "Evento",
            {
                "fields": [
                    "acreditacion",
                    "restricciones_alimentarias",
                    "detalle_restricciones_alimentarias",
                    "talla_camiseta",
                    "fecha_registro",
                    "fecha_verificacion_correo",
                    "fecha_aceptacion",
                    "fecha_confirmacion_plaza",
                    "fecha_rechazo_plaza",
                    "motivo_error_correo_verificacion",
                    "motivacion",
                    "notas",
                ]
            },
        ),
    ]

    readonly_fields = [
        "cv",
        "fecha_registro",
        "fecha_verificacion_correo",
        "fecha_aceptacion",
        "fecha_confirmacion_plaza",
        "fecha_rechazo_plaza",
        "motivo_error_correo_verificacion",
    ]

    list_display = [
        "correo",
        "nombre",
        "ciudad",
        "fecha_registro",
        "verificado",
        "aceptado",
        "confirmado",
        "rechazo",
        "error_verificacion",
    ]
    list_filter = [
        EstadoPersonaListFilter,
        "ciudad",
    ]

    search_fields = [
        "correo",
        "nombre",
    ]

    actions = [
        aceptar_personas,
        reenviar_correo_verificacion,
        reenviar_correo_confirmacion,
    ]

    inlines = [
        TokenInline,
    ]

    def change_view(self, request, object_id, form_url="", extra_context=None):
        personal_fields = self.fieldsets[0][1]["fields"]

        # Permiso para ver el CV
        if request.user.has_perm("gestion.ver_cv_mentor"):
            if "cv" not in personal_fields:
                personal_fields.insert(5, "cv")
        if not request.user.has_perm("gestion.ver_cv_mentor"):
            if "cv" in personal_fields:
                personal_fields.remove("cv")
                logger.debug(f"{request.user.username} no tiene permiso para ver CVs.")

        # Permiso para ver DNI y teléfono
        if request.user.has_perm("gestion.ver_dni_telefono_mentor"):
            if "dni" not in personal_fields:
                personal_fields.insert(5, "dni")
            if "telefono" not in personal_fields:
                personal_fields.insert(5, "telefono")
        if not request.user.has_perm("gestion.ver_dni_telefono_mentor"):
            if "dni" in personal_fields:
                personal_fields.remove("dni")
                logger.debug(f"{request.user.username} no tiene permiso para ver DNIs.")

            if "telefono" in personal_fields:
                personal_fields.remove("telefono")
                logger.debug(
                    f"{request.user.username} no tiene permiso para ver teléfonos."
                )

        return super(MentorAdmin, self).change_view(
            request, object_id, form_url, extra_context
        )

    def has_aceptar_permission(self, request):
        return request.user.has_perm("gestion.aceptar_mentor")

    def has_reenviar_verificacion_permission(self, request):
        return request.user.has_perm("gestion.reenviar_verificacion")

    def has_reenviar_confirmacion_permission(self, request):
        return request.user.has_perm("gestion.reenviar_confirmacion")


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
        "usado",
    ]
    list_filter = [
        "tipo",
        TokenValidoListFilter,
        TokenUsadoListFilter,
    ]

    search_fields = [
        "persona__nombre",
        "persona__correo",
        "token",
    ]

    def view_on_site(self, obj):
        if not obj.fecha_uso:
            return None

        if obj.tipo == "VERIFICACION":
            return reverse("verificar-correo", kwargs={"token": obj.token})
        elif obj.tipo == "CONFIRMACION":
            return reverse("confirmar-plaza", kwargs={"token": obj.token})

        return None


class ColaboradorAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            "Personal",
            {
                "fields": [
                    "nombre",
                    "correo",
                    "dni",
                    "empresa",
                    "restricciones_alimentarias",
                    "detalle_restricciones_alimentarias",
                ]
            },
        ),
        (
            "Evento",
            {
                "fields": [
                    "acreditacion",
                    "comidas",
                    "notas",
                ]
            },
        ),
    ]

    list_display = ["correo", "nombre", "empresa"]

    list_filter = ["empresa", "comidas"]

    search_fields = ["correo", "nombre"]


# Register your models here.
admin.site.register(Colaborador, ColaboradorAdmin)
admin.site.register(Mentor, MentorAdmin)
admin.site.register(Participante, ParticipanteAdmin)
admin.site.register(RestriccionAlimentaria)
admin.site.register(Presencia)
admin.site.register(TipoPase)
admin.site.register(Pase)
admin.site.register(Token, TokenAdmin)
admin.site.register(Empresa)
