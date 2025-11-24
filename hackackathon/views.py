# Copyright (C) 2025-now  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest
from django.shortcuts import redirect
from django.utils import translation
from django.utils.translation import gettext_lazy as _


def idioma(request: HttpRequest, codigo: str):
    idiomas_validos = [codigo for codigo, nombre in settings.LANGUAGES]

    if codigo in idiomas_validos:
        translation.activate(codigo)
    else:
        messages.error(
            request,
            _("Código de idioma no válido. Los posibles son")
            + ": "
            + ", ".join(idiomas_validos),
        )

    if siguiente := request.GET.get("next"):
        return redirect(siguiente)

    return redirect("registro")
