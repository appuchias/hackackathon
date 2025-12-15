# Copyright (C) 2025-now  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from hackackathon import views

admin.site.site_header = "Hackackathon Admin"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("idioma/<codigo>", views.idioma, name="idioma"),
    path("", include("gestion.urls")),
]

# Válido durante el desarrollo
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
