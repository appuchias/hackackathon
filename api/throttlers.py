# Copyright (C) 2025-now  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

from django.conf import settings
from rest_framework.throttling import UserRateThrottle


class BurstStatsThrottler(UserRateThrottle):
    """
    Clase para limitar las peticiones a los endpoints de estadísticas.

    Implementada por el mayor coste de BD que conllevan
    Permite todas las peticiones de superusuarios y limita las demás al valor de STATS_THROTTLE_RATE
    """

    rate = settings.STATS_THROTTLE_RATE

    def allow_request(self, request, view):
        if request.user.is_superuser:
            return True

        return super().allow_request(request, view)

