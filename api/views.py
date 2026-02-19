# Copyright (C) 2025-now  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

from django.db.models import OuterRef, Subquery
from django.http import JsonResponse
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.exceptions import MethodNotAllowed, ValidationError
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet, ModelViewSet

from api.serializers import (
    AsignarAcreditacionSerializer,
    PaseSerializer,
    PresenciaSerializer,
    RestriccionAlimentariaSerializer,
    TipoPaseSerializer,
    VerPersonaSerializer,
    PersonaReducidaSerializer,
)
from api.throttlers import BurstStatsThrottler
from gestion.models import (
    Mentor,
    Pase,
    Persona,
    Presencia,
    RestriccionAlimentaria,
    TipoPase,
    Participante,
)


class PersonaList(ListAPIView):
    """
    Ruta para obtener Personas por correo o acreditación.
    """

    serializer_class = VerPersonaSerializer

    def get_queryset(self):
        correo = self.request.query_params.get("correo")
        acreditacion = self.request.query_params.get("acreditacion")

        queryset = Persona.objects.all()

        # Permitir correo o acreditación
        if correo:
            queryset = queryset.filter(correo=correo)
        if acreditacion:
            queryset = queryset.filter(acreditacion=acreditacion)

        return queryset

    def get_serializer_class(self):
        correo = self.request.query_params.get("correo")
        acreditacion = self.request.query_params.get("acreditacion")

        if not correo and not acreditacion:
            return PersonaReducidaSerializer

        return super().get_serializer_class()


class PersonaRetrieveUpdate(RetrieveUpdateAPIView):
    queryset = Persona.objects.all()
    serializer_class = VerPersonaSerializer

    lookup_field = "correo"

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return AsignarAcreditacionSerializer

        return super().get_serializer_class()

    def put(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT")

    def update(self, request, *args, **kwargs):
        print(request)
        return super(PersonaRetrieveUpdate, self).update(request, *args, **kwargs)


class TipoPaseViewSet(ReadOnlyModelViewSet):
    """
    Ruta de la API que permite ver los Tipos de Pase disponibles.
    """

    queryset = TipoPase.objects.all().order_by("inicio_validez")
    serializer_class = TipoPaseSerializer


class RestriccionAlimentariaViewSet(ReadOnlyModelViewSet):
    """
    Ruta de la API que permite ver el mapa de Restricciones Alimentarias.
    """

    queryset = RestriccionAlimentaria.objects.all().order_by("nombre")
    serializer_class = RestriccionAlimentariaSerializer


class PaseViewSet(ListModelMixin, CreateModelMixin, RetrieveModelMixin, GenericViewSet):
    """
    Ruta de la API que permite ver, crear y modificar pases.
    """

    serializer_class = PaseSerializer

    def get_queryset(self):
        queryset = Pase.objects.all().order_by("-fecha")

        filterset_fields = ("persona",)
        for field in filterset_fields:
            if value := self.request.query_params.get(field):
                queryset = queryset.filter(**{field: value})

        return queryset


class PresenciaViewSet(ModelViewSet):
    """
    Ruta de la API que permite ver, crear y modificar presencias.
    """

    serializer_class = PresenciaSerializer

    def get_queryset(self):
        queryset = Presencia.objects.all().order_by("-entrada")

        filterset_fields = ("persona",)
        for field in filterset_fields:
            if value := self.request.query_params.get(field):
                queryset = queryset.filter(**{field: value})

        return queryset

    def destroy(self, request, *args, **kwargs):
        return MethodNotAllowed("DELETE")


class StatsView(ListAPIView):

    throttle_classes = [BurstStatsThrottler]

    def list(self, request, *args, **kwargs):
        stats = dict()

        # Subconsulta para obtener el valor de la salida de la última presencia de una persona
        ultima_presencia_salida = (
            Presencia.objects.filter(persona=OuterRef("pk"))
            .order_by("-id_presencia")
            .values("salida")[:1]
        )

        participantes = Participante.objects.all()
        participantes_acreditados = participantes.filter(acreditacion__isnull=False)
        participantes_dentro = participantes_acreditados.annotate(
            ultima_presencia_salida=Subquery(ultima_presencia_salida)
        ).filter(ultima_presencia_salida__isnull=True)

        stats["participantes"] = {
            "total": participantes.count(),
            "acreditados": participantes_acreditados.count(),
            "dentro": participantes_dentro.count(),
        }

        mentores = Mentor.objects.all()
        mentores_acreditados = mentores.filter(acreditacion__isnull=False)
        mentores_dentro = mentores_acreditados.annotate(
            ultima_presencia_salida=Subquery(ultima_presencia_salida)
        ).filter(ultima_presencia_salida__isnull=True)

        stats["mentores"] = {
            "total": mentores.count(),
            "acreditados": mentores_acreditados.count(),
            "dentro": mentores_dentro.count(),
        }

        return JsonResponse(stats)


# class PresenciaAccion(APIView):
#     serializer_class = PresenciaSerializer
#
#     def get(self, request, *args, **kwargs):
#         acreditacion = request.query_params.get("acreditacion")
#         accion = request.query_params.get("accion")
#
#         if not acreditacion or not accion:
#             raise ValidationError("Es necesario especificar 'acreditacion' y 'accion'")
#
#         print(acreditacion, accion)
#
#         persona = Persona.objects.get(acreditacion=acreditacion)
#
#         presencias = Presencia.objects.filter(persona=persona)
#         ultima = presencias.order_by("-entrada").first()
#
#         if accion == "ENTRADA":
#             # if not ultima.salida:
#             #     messages.warning(request, "No hay salida registrada de la última presencia")
#
#             # Guardar entrada
#             entrada = Presencia(persona=persona, entrada=timezone.now())
#             entrada.save()
#
#         elif accion == "SALIDA":
#             if not ultima:
#                 # messages.error(request, "No había ninguna entrada")
#                 ultima = Presencia(persona=persona)
#             elif ultima.salida:
#                 # messages.warning(request, "La última presencia ya tiene salida registrada")
#                 ultima = Presencia(persona=persona)
#
#             # Guardar salida
#             ultima.salida = timezone.now()
#             ultima.save()
#
#         else:
#             raise ParseError
#
#         return Response(Presencia.objects.filter(persona=persona))
