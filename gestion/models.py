# Copyright (C) 2025-now  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

from datetime import timedelta
from uuid import uuid4

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.validators import (
    FileExtensionValidator,
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.utils import timezone

GENEROS = (
    ("HOMBRE", "Hombre"),
    ("MUJER", "Mujer"),
    ("OTRO", "Otro"),
)

TALLAS_CAMISETA = (
    ("S", "S"),
    ("M", "M"),
    ("L", "L"),
    ("XL", "XL"),
    ("XXL", "XXL"),
)

NIVELES_ESTUDIO = (
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
    return f"cv/{instance.dni}_{instance.correo.replace("@", "-").replace(".", "-")}_pendiente.pdf"


def validador_pdf(value):
    if value.file.content_type != "application/pdf":
        raise ValidationError("El archivo no es un PDF")


class PersonaAbstracta(models.Model):
    correo = models.EmailField(max_length=254, unique=True, primary_key=True)
    nombre = models.CharField(max_length=100)
    notas = models.TextField(null=True, blank=True)
    acreditacion = models.CharField(
        max_length=8, unique=True, null=True, blank=True, default=None
    )

    restricciones_alimentarias = models.ManyToManyField(
        "RestriccionAlimentaria",
        blank=True,
        related_name="%(class)ss",
    )

    class Meta:
        abstract = True


class Patrocinador(PersonaAbstracta):
    empresa = models.CharField(max_length=100)

    class Meta(PersonaAbstracta.Meta):
        verbose_name = "Patrocinador"
        verbose_name_plural = "Patrocinadores"

    def __str__(self):
        return f"{self.empresa}: {self.nombre}"


# Create your models here.
class Persona(PersonaAbstracta):
    dni = models.CharField(max_length=9, unique=True, null=True)
    genero = models.CharField(max_length=10, choices=GENEROS, null=True)
    talla_camiseta = models.CharField(max_length=10, choices=TALLAS_CAMISETA, null=True)

    cv = models.FileField(
        upload_to=ruta_cv,
        null=True,
        validators=[FileExtensionValidator(["pdf"]), validador_pdf],
    )
    compartir_cv = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_verificacion_correo = models.DateTimeField(
        null=True, blank=True, default=None
    )
    fecha_aceptacion = models.DateTimeField(null=True, blank=True, default=None)
    fecha_confirmacion_plaza = models.DateTimeField(null=True, blank=True, default=None)

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

    def __str__(self):
        return f"{self.nombre} ({self.correo})"

    class Meta:
        ordering = ["-fecha_registro"]


class Mentor(Persona):

    class Meta(Persona.Meta):
        verbose_name = "Mentor"
        verbose_name_plural = "Mentores"

    def __str__(self):
        return f"{self.nombre}"


class Participante(Persona):
    telefono = models.CharField(max_length=16, null=True)
    ano_nacimiento = models.PositiveIntegerField(
        null=True,
        validators=[
            MinValueValidator(1970, "El año debe ser mayor o igual a 1970."),
            MaxValueValidator(2015, "El año debe ser menor o igual a 2015."),
        ],
    )
    nivel_estudio = models.CharField(null=True, max_length=128, choices=NIVELES_ESTUDIO)
    nombre_estudio = models.CharField(max_length=128, null=True)
    centro_estudio = models.CharField(max_length=128, null=True)
    curso = models.CharField(max_length=128, null=True)
    ciudad = models.CharField(max_length=128, null=True)
    quiere_creditos = models.BooleanField(default=False)
    motivacion = models.TextField(null=True)

    class Meta(Persona.Meta):
        verbose_name = "Participante"
        verbose_name_plural = "Participantes"

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
    inicio_validez = models.DateTimeField()

    class Meta:
        verbose_name = "Tipo de Pase"
        verbose_name_plural = "Tipos de Pase"
        ordering = ["inicio_validez"]

    def __str__(self):
        return f"{self.nombre} (Desde {self.inicio_validez})"


class Pase(models.Model):
    id_pase = models.AutoField(primary_key=True)
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name="pases")
    tipo_pase = models.ForeignKey(
        TipoPase, on_delete=models.CASCADE, related_name="pases"
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
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField(null=False)
    fecha_uso = models.DateTimeField(null=True, blank=True, default=None)

    @admin.display(boolean=True, ordering="fecha_creacion", description="Usado")
    def usado(self):
        return self.fecha_uso is not None

    @admin.display(boolean=True, ordering="fecha_creacion", description="Válido")
    def valido(self):
        return self.fecha_expiracion > timezone.now() and not self.usado()

    def __str__(self):
        return f"Token de {self.persona.nombre}"
