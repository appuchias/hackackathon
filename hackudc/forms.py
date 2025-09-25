from datetime import datetime

from django import forms

from hackudc.models import Participante, RestriccionAlimentaria, TipoPase


class ParticipanteForm(forms.ModelForm):
    class Meta:
        model = Participante
        fields = [
            "nombre",
            "correo",
            "dni",
            "genero",
            "restricciones_alimentarias",
            "telefono",
            "ano_nacimiento",
            "nivel_estudio",
            "nombre_estudio",
            "centro_estudio",
            "curso",
            "ciudad",
            "quiere_creditos",
            "talla_camiseta",
            "cv",
            "compartir_cv",
            "motivacion",
            "notas",
        ]

        labels = {
            "dni": "DNI",
            "genero": "Género",
            "restricciones_alimentarias": "Restricciones alimentarias",
            "ano_nacimiento": "Año de nacimiento",
            "nivel_estudio": "Nivel actual de estudios",
            "nombre_estudio": "Nombre de los estudios",
            "centro_estudio": "Centro de estudios",
            "curso": "Curso (si aplica)",
            "ciudad": "Ciudad de residencia",
            "quiere_creditos": "¿Quieres solicitar créditos?",
            "talla_camiseta": "Talla de camiseta",
            "cv": "CV",
            "compartir_cv": "¿Autorizas compartir tu CV con los patrocinadores?",
            "motivacion": "Motivación para participar en el HackUDC",
            "notas": "Notas",
        }

        help_texts = {
            "cv": "Currículum vitae en formato PDF. Lo usaremos para conocerte mejor y lo haremos llegar a nuestros patrocinadores si lo deseas.",
            "notas": "Otros datos que consideres relevantes (alergias, etc.).",
        }

        widgets = {
            "restricciones_alimentarias": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["restricciones_alimentarias"].queryset = (
            RestriccionAlimentaria.objects.all().order_by("id_restriccion")
        )


class Registro(forms.Form):
    persona = forms.CharField(label="Correo a registrar", max_length=100)
    acreditacion = forms.CharField(
        label="Acreditación a asignar", max_length=6, required=False
    )


class PaseForm(forms.Form):
    # No funciona siempre el valor inicial. Indicarlo en la vista va bien
    # tipo_pase = forms.ModelChoiceField(
    #     queryset=TipoPase.objects.all().order_by("inicio_validez"),
    #     initial=TipoPase.objects.filter(inicio_validez__lte=datetime.now())
    #     .order_by("inicio_validez")
    #     .last(),
    # )
    tipo_pase = forms.ModelChoiceField(
        queryset=TipoPase.objects.all().order_by("inicio_validez")
    )
    participante = forms.CharField(label="Acreditación", max_length=6)


class PresenciaForm(forms.Form):
    accion = forms.ChoiceField(
        choices=(("v", "Ver"), ("e", "Entrada"), ("s", "Salida"))
    )
    participante = forms.CharField(label="Acreditación a asignar", max_length=6)
