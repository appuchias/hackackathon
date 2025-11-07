from datetime import datetime, timedelta

from django.core.management import BaseCommand
from django.core.mail import EmailMessage
from django.utils import timezone

from hackudc.models import Participante, Token


class Command(BaseCommand):
    help = (
        "Envía un correo de confirmación a los participantes aceptados no confirmados"
    )

    def handle(self, *args, **options):
        participantes = Participante.objects.filter(
            fecha_aceptacion__isnull=False, fecha_confirmacion_plaza__isnull=True
        )

        for participante in participantes:
            token = Token(
                tipo="CONFIRMACION",
                persona=participante,
                fecha_expiracion=timezone.now() + timedelta(days=14),
            )
            token.save()

            try:
                email = EmailMessage(
                    "PLAZA",
                    str(token.token),
                    to=(participante.correo,),
                    reply_to=("info@gpul.org",),
                    headers={
                        "Message-ID": f"hackudc-{token.fecha_creacion.timestamp()}"
                    },
                )
                email.send(fail_silently=False)
            except ConnectionRefusedError:
                self.stdout.write(self.style.ERROR("Error al mandar un correo"))
                break
            self.stdout.write(self.style.SUCCESS("Mensajes enviados"))
