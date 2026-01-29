# Copyright (C) 2025-now  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

from rest_framework import serializers

from gestion.models import (
    Pase,
    Persona,
    Presencia,
    RestriccionAlimentaria,
    TipoPase,
)


class RestriccionAlimentariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestriccionAlimentaria
        fields = ["id_restriccion", "nombre"]


class VerPersonaSerializer(serializers.ModelSerializer):
    restricciones_alimentarias = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True
    )

    class Meta:
        model = Persona
        fields = [
            "correo",
            "nombre",
            "dni",
            "restricciones_alimentarias",
            "detalle_restricciones_alimentarias",
            "compartir_cv",
            "talla_camiseta",
            "fecha_registro",
            "fecha_verificacion_correo",
            "fecha_aceptacion",
            "fecha_confirmacion_plaza",
            "acreditacion",
            "notas",
        ]
        read_only_fields = [
            "fecha_registro",
            "fecha_verificacion_correo",
            "fecha_aceptacion",
            "fecha_confirmacion_plaza",
        ]


class AsignarAcreditacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = ["correo", "acreditacion"]


class TipoPaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoPase
        fields = "__all__"
        # fields = ["id_tipo_pase", "nombre", "inicio_validez"]


class PaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pase
        fields = "__all__"
        # fields = ["id_pase", "fecha", "persona", "tipo_pase"]
        # depth = 1  # 0 = Solo PK


class PresenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presencia
        fields = "__all__"
        # fields = ["id_presencia", "persona", "entrada", "salida"]
