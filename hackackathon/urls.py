# Copyright (C) 2025-2026  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Hackackathon Admin"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("gestion.urls")),
    path("api/", include("api.urls")),
]

# Válido durante el desarrollo
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += debug_toolbar_urls()
