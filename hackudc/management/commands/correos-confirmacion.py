from datetime import datetime

from django.core.management.base import BaseCommand
from django.core.mail import send_mail

from hackudc.models import Participante, Token


class Command(BaseCommand):
    help = "Envía un correo de confirmación a los usuarios aceptados no confirmados"

    def handle(self, *args, **options):
        participantes = (
            Participante.objects.filter(aceptado=True).filter(confirmado=False).all()
        )

        for participante in participantes:
            print(participante)
            token = Token(persona=participante, fecha=datetime.now())
            token.save()

            send_mail(
                "HackUDC 2026 - ¡Estás dentro!",
                f"Hola {participante.nombre}. Toka tu otro token {token.uuid}",
                "no-reply@gpul.org",
                (participante.correo,),
                fail_silently=False,
            )
