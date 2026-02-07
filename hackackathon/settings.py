# Copyright (C) 2025-2026  p.fernandezf <p@fernandezf.es> & iago.rivas <delthia@delthia.com>

import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

SECRET_KEY_FALLBACKS = [
    os.getenv("SECRET_KEY_FALLBACK"),
]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Host de la web de registro
HOST_REGISTRO = os.getenv("HOST_REGISTRO")

ALLOWED_HOSTS = [HOST_REGISTRO]
if DEBUG:
    ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    "https://" + HOST_REGISTRO,
]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "gestion",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.auth.middleware.LoginRequiredMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "hackackathon.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "hackackathon.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Logging
# https://docs.djangoproject.com/en/5.2/howto/logging/
LOGFILE_NAME = "log/"
LOGFILE_SIZE = 10 * 1024**2  # 10 MB
LOGFILE_COUNT = 2
LOGGING = {
    "version": 1,  # the dictConfig format version
    "disable_existing_loggers": False,  # retain the default loggers
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "con_correo": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] (%(correo)s) %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "django.server": {  # manage.py runserver
            "()": "django.utils.log.ServerFormatter",
            "format": "[{server_time}] {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
        },
        "django.server": {  # manage.py runserver
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
            "include_html": True,
        },
        # Django extra
        "null": {
            "class": "logging.NullHandler",
        },
        # Custom
        "file_debug": {
            "class": "logging.FileHandler",
            "formatter": "standard",
            "filename": LOGFILE_NAME + "debug.log",
        },
        "file_info": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "formatter": "standard",
            "filename": LOGFILE_NAME + "info.log",
        },
        "file_warning": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "formatter": "standard",
            "filename": LOGFILE_NAME + "warning.log",
        },
        "file_error": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "formatter": "standard",
            "filename": LOGFILE_NAME + "error.log",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "mail_admins"],
            "level": "INFO",
        },
        "django.server": {  # manage.py runserver
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": False,
        },
        # Django extra
        "django.security.DisallowedHost": {
            "handlers": ["null"],
            "propagate": False,
        },
        "django.utils.autoreload": {
            "handlers": ["console"],
            "propagate": False,
        },
        # Custom
        "": {
            "level": os.getenv("DJANGO_LOG_LEVEL", "DEBUG"),
            "handlers": ["file_error", "file_warning", "file_info", "file_debug"],
        },
        "hackackathon": {
            "level": "DEBUG",
            "handlers": ["file_debug"],
        },
        "gestion": {
            "level": "DEBUG",
            "handlers": ["file_debug"],
        },
        # Custom/con_correo
        "gestion.utils": {
            "level": "DEBUG",
            "formatter": "con_correo",
            "handlers": ["file_debug"],
        },
        "gestion.management.commands.correosconfirmacion": {
            "level": "DEBUG",
            "formatter": "con_correo",
            "handlers": ["file_debug"],
        },
    },
}


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "es-es"

TIME_ZONE = "Europe/Madrid"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"
STATICFILES_DIRS = [
    BASE_DIR / "staticfiles",
]

# Media files (User uploaded content)
# https://docs.djangoproject.com/en/5.1/topics/files/
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "media/"

# Fixtures (initial data)
# https://docs.djangoproject.com/en/5.1/topics/db/fixtures/
FIXTURE_DIRS = [
    BASE_DIR / "fixtures",
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Login
# https://docs.djangoproject.com/en/5.1/ref/settings/#login-url
LOGIN_URL = "/login"

# Messages
# https://docs.djangoproject.com/en/5.1/ref/contrib/messages/
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

# Email
# https://docs.djangoproject.com/en/5.1/topics/email/
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

EMAIL_MESSAGE_RATE = 10  # Máximo de emails por segundo en la confirmación de correo
EMAIL_MAX_ERRORS = 5  # Máximo de errores en el envío de correos de confirmación

SERVER_EMAIL = os.getenv("SERVER_EMAIL")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Configuración de entorno ----------------------------------------------------
# Inicio del evento
FECHA_INICIO_EVENTO = datetime.fromisoformat(os.getenv("FECHA_INICIO_EVENTO")).replace(
    tzinfo=ZoneInfo(TIME_ZONE)
)
# Fin del evento
FECHA_FIN_EVENTO = datetime.fromisoformat(os.getenv("FECHA_FIN_EVENTO")).replace(
    tzinfo=ZoneInfo(TIME_ZONE)
)
# Fin del plazo de registro
FECHA_FIN_REGISTRO = datetime.fromisoformat(os.getenv("FECHA_FIN_REGISTRO")).replace(
    tzinfo=ZoneInfo(TIME_ZONE)
)

# Nombre y mail del administrador
NOMBRE_ADMIN = os.getenv("NOMBRE_ADMIN")
MAIL_ADMIN = os.getenv("MAIL_ADMIN")

# Asuntos de los correos
EMAIL_VERIFICACION_ASUNTO = "HackUDC 2026 - Confirma tu correo ✉️"
EMAIL_CONFIRMACION_ASUNTO = "HackUDC 2026 - Confirma tu plaza! 🎄"
EMAIL_VERIFICACION_CORRECTA_ASUNTO = "HackUDC 2026 - Solicitud registrada correctamente"
EMAIL_ACEPTACION_ASUNTO = "HackUDC 2026 - Plaza confirmada"
EMAIL_RECHAZO_ASUNTO = "HackUDC 2026 - Plaza rechazada"
EMAIL_COLABORADOR_ASUNTO = "HackUDC 2026 - Solicitud recibida"
# -----------------------------------------------------------------------------

ADMINS = [
    (NOMBRE_ADMIN, MAIL_ADMIN),
]
