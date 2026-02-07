# Copyright (C) 2025-2026  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

import logging
from uuid import uuid4

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)

GENEROS = (
    (None, ""),
    ("H", "Hombre"),
    ("M", "Mujer"),
    ("O", "Otro"),
    ("-", "Prefiero no decirlo"),
)

TALLAS_CAMISETA = (
    (None, ""),
    ("S", "S"),
    ("M", "M"),
    ("L", "L"),
    ("XL", "XL"),
    ("2XL", "2XL"),
    ("3XL", "3XL"),
)

NIVELES_ESTUDIO = (
    (None, ""),
    ("FORMACION_PROFESIONAL", "Formación Profesional"),
    ("UNIVERSIDAD", "Universidad"),
    ("MASTER", "Máster"),
    ("OTRO", "Otro (Especificar en notas)"),
)

TIPOS_TOKEN = (
    ("VERIFICACION", "Verificación correo"),
    ("CONFIRMACION", "Confirmación plaza"),
)


def ruta_cv(instance, filename):
    correo = instance.correo.replace("@", "-").replace(".", "-")
    return f"cv/{instance.dni}_{correo}.pdf"


def validador_pdf(value):
    if value.file.content_type != "application/pdf":
        logger.debug(f"Se ha subido un CV inválido (no es un PDF).")
        raise ValidationError("El archivo no es un PDF")


class PersonaAbstracta(models.Model):
    correo = models.EmailField(max_length=254, unique=True, primary_key=True)
    nombre = models.CharField(max_length=100, verbose_name="Nombre completo")
    notas = models.TextField(null=True, blank=True)
    acreditacion = models.CharField(
        max_length=8,
        unique=True,
        null=True,
        blank=True,
        default=None,
        verbose_name="Acreditación",
    )

    restricciones_alimentarias = models.ManyToManyField(
        "RestriccionAlimentaria",
        blank=True,
        related_name="%(class)ss",
    )
    detalle_restricciones_alimentarias = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        verbose_name="Detalles sobre las restricciones alimentarias",
    )

    class Meta:
        abstract = True


class Empresa(models.Model):
    id_empresa = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Colaborador(PersonaAbstracta):
    notas = models.TextField(null=True, blank=True)
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
    )
    comidas = models.ManyToManyField("TipoPase", blank=True)

    # Parte de Persona
    dni = models.CharField(max_length=9, unique=True, null=False, verbose_name="DNI")
    telefono = models.CharField(
        max_length=16, null=True, blank=True, verbose_name="Teléfono"
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de registro"
    )

    class Meta(PersonaAbstracta.Meta):
        ordering = ["correo"]
        verbose_name = "Colaborador"
        verbose_name_plural = "Colaboradores"

    def __str__(self):
        return f"{self.empresa}: {self.nombre}"


class Persona(PersonaAbstracta):
    dni = models.CharField(max_length=9, unique=True, null=False, verbose_name="DNI")
    genero = models.CharField(
        max_length=10, choices=GENEROS, null=False, verbose_name="Género"
    )
    talla_camiseta = models.CharField(
        max_length=10,
        choices=TALLAS_CAMISETA,
        null=False,
        verbose_name="Talla de la camiseta",
    )

    cv = models.FileField(
        upload_to=ruta_cv,
        null=True,
        validators=[FileExtensionValidator(["pdf"]), validador_pdf],
        verbose_name="CV",
    )
    compartir_cv = models.BooleanField(
        default=False, verbose_name="Autoriza a compartir el CV"
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de registro"
    )
    fecha_verificacion_correo = models.DateTimeField(
        null=True,
        blank=True,
        default=None,
        verbose_name="Fecha de verificación del correo",
    )
    fecha_aceptacion = models.DateTimeField(
        null=True, blank=True, default=None, verbose_name="Fecha de aceptación"
    )
    fecha_confirmacion_plaza = models.DateTimeField(
        null=True,
        blank=True,
        default=None,
        verbose_name="Fecha de confirmación de la plaza",
    )
    fecha_rechazo_plaza = models.DateTimeField(
        null=True,
        blank=True,
        default=None,
        verbose_name="Fecha de rechazo de la plaza",
    )
    motivo_error_correo_verificacion = models.TextField(
        max_length=4096,
        null=True,
        blank=True,
        default=None,
        verbose_name="Motivo del error en el envío del correo de verificación",
    )

    @admin.display(
        boolean=True,
        ordering="fecha_registro",
        description="Error de verificación de correo",
    )
    def error_verificacion(self):
        return (
            self.motivo_error_correo_verificacion is not None
            and self.fecha_verificacion_correo is None
        )

    @admin.display(
        boolean=True, ordering="fecha_verificacion_correo", description="Verificado"
    )
    def verificado(self):
        return self.fecha_verificacion_correo is not None

    @admin.display(boolean=True, ordering="fecha_aceptacion", description="Aceptado")
    def aceptado(self):
        return self.fecha_aceptacion is not None

    @admin.display(
        boolean=True, ordering="fecha_confirmacion_plaza", description="Confirmado"
    )
    def confirmado(self):
        return self.fecha_confirmacion_plaza is not None

    @admin.display(boolean=True, ordering="fecha_rechazo_plaza", description="Rechazo")
    def rechazo(self):
        return self.fecha_rechazo_plaza is not None

    def __str__(self):
        return f"{self.nombre} ({self.correo})"

    class Meta:
        ordering = ["-fecha_registro"]

        permissions = [
            ("reenviar_verificacion", "Reenviar el correo de verificación"),
            ("reenviar_confirmacion", "Reenviar el correo de confirmación"),
        ]


class Mentor(Persona):
    telefono = models.CharField(max_length=16, null=False, verbose_name="Teléfono")
    fecha_nacimiento = models.DateField(null=False, verbose_name="Fecha de nacimiento")
    ciudad = models.CharField(
        max_length=128, null=True, verbose_name="Ciudad de residencia"
    )
    motivacion = models.TextField(null=True, verbose_name="Motivación")

    class Meta(Persona.Meta):
        verbose_name = "Mentor"
        verbose_name_plural = "Mentores"

        permissions = [
            ("aceptar_mentor", "Aceptar Mentor"),
            ("ver_cv_mentor", "Ver el CV de Mentor"),
            (
                "ver_dni_telefono_mentor",
                "Ver el DNI y el teléfono de Mentor",
            ),
        ]

    def __str__(self):
        return f"{self.nombre}"


class Participante(Persona):
    telefono = models.CharField(max_length=16, null=False, verbose_name="Teléfono")
    fecha_nacimiento = models.DateField(null=False, verbose_name="Fecha de nacimiento")
    nivel_estudio = models.CharField(
        null=False,
        max_length=128,
        choices=NIVELES_ESTUDIO,
        verbose_name="Nivel actual de estudios",
    )
    nombre_estudio = models.CharField(
        max_length=128, null=True, verbose_name="Nombre de los estudios"
    )
    centro_estudio = models.CharField(
        max_length=128, null=True, verbose_name="Centro de estudios"
    )
    curso = models.CharField(
        max_length=128, null=True, blank=True, verbose_name="Curso actual (si aplica)"
    )
    ciudad = models.CharField(
        max_length=128, null=True, verbose_name="Ciudad de residencia"
    )
    quiere_creditos = models.BooleanField(
        default=False, verbose_name="Quiere créditos?"
    )
    motivacion = models.TextField(null=True, verbose_name="Motivación")

    class Meta(Persona.Meta):
        verbose_name = "Participante"
        verbose_name_plural = "Participantes"

        permissions = [
            ("aceptar_participante", "Aceptar Participante"),
            ("ver_cv_participante", "Ver el CV de Participante"),
            (
                "ver_dni_telefono_participante",
                "Ver el DNI y el teléfono de Participante",
            ),
        ]

    def __str__(self):
        return f"{self.nombre} ({'No aceptado' if not self.fecha_aceptacion else 'Aceptado'})"


class RestriccionAlimentaria(models.Model):
    id_restriccion = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Restricción Alimentaria"
        verbose_name_plural = "Restricciones Alimentarias"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Presencia(models.Model):
    id_presencia = models.AutoField(primary_key=True)
    persona = models.ForeignKey(
        Persona, on_delete=models.CASCADE, related_name="tiempo_acceso"
    )
    entrada = models.DateTimeField(null=True, blank=True, default=None)
    salida = models.DateTimeField(null=True, blank=True, default=None)

    class Meta:
        verbose_name = "Presencia"
        verbose_name_plural = "Presencias"

        unique_together = ("persona", "entrada", "salida")

    def __str__(self):
        return f"Presencia de {self.persona.nombre} desde {self.entrada} hasta {self.salida}"


class TipoPase(models.Model):
    id_tipo_pase = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    inicio_validez = models.DateTimeField(verbose_name="Inicio de la validez")

    class Meta:
        verbose_name = "Tipo de Pase"
        verbose_name_plural = "Tipos de Pase"
        ordering = ["inicio_validez"]

    def __str__(self):
        return f"{self.nombre}"


class Pase(models.Model):
    id_pase = models.AutoField(primary_key=True)
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name="pases")
    tipo_pase = models.ForeignKey(
        TipoPase,
        on_delete=models.CASCADE,
        related_name="pases",
        verbose_name="Tipo de pase",
    )
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pase"
        verbose_name_plural = "Pases"
        ordering = ["fecha"]

        unique_together = ("persona", "tipo_pase", "fecha")

    def __str__(self):
        return f"Pase '{self.tipo_pase}' de {self.persona.nombre} - {self.tipo_pase.nombre} ({self.fecha})"


class Token(models.Model):
    token = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    tipo = models.CharField(max_length=50, choices=TIPOS_TOKEN)
    persona = models.ForeignKey(
        Persona, on_delete=models.CASCADE, related_name="tokens"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación"
    )
    fecha_expiracion = models.DateTimeField(
        null=False, verbose_name="Fecha de expiración"
    )
    fecha_uso = models.DateTimeField(
        null=True, blank=True, default=None, verbose_name="Fecha de uso"
    )

    @admin.display(boolean=True, ordering="fecha_creacion", description="Usado")
    def usado(self):
        return self.fecha_uso is not None

    @admin.display(boolean=True, ordering="fecha_creacion", description="Válido")
    def valido(self):
        return self.fecha_expiracion > timezone.now() and not self.usado()

    def __str__(self):
        return f"Token de {self.tipo.capitalize()} de {self.persona.nombre}"
