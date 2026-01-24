# Copyright (C) 2025-now  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.exceptions import MethodNotAllowed, ValidationError
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet, ModelViewSet

from api.serializers import (
    AsignarAcreditacionSerializer,
    PaseSerializer,
    PresenciaSerializer,
    TipoPaseSerializer,
    VerPersonaSerializer,
)
from gestion.models import Pase, Persona, Presencia, TipoPase


class PersonaList(ListAPIView):
    """
    Ruta para obtener Personas por correo o acreditación.
    """

    serializer_class = VerPersonaSerializer

    def get_queryset(self):
        correo = self.request.query_params.get("correo")
        acreditacion = self.request.query_params.get("acreditacion")

        if not correo and not acreditacion:
            raise ValidationError(
                "Es necesario especificar 'correo' o 'acreditacion' para realizar la búsqueda."
            )

        queryset = Persona.objects.all()

        # Permitir correo o acreditación
        if correo:
            queryset = Persona.objects.filter(correo=correo)
        if acreditacion:
            queryset = Persona.objects.filter(acreditacion=acreditacion)

        return queryset


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
