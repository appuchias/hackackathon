import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# Fin plazo registro
PLAZO_REGISTRO = "2025-12-31 23:59:59+01:00"

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

SECRET_KEY_FALLBACKS = [
    os.getenv("SECRET_KEY_FALLBACK"),
]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

if DEBUG:
    ALLOWED_HOSTS = ["*"]

# CSRF_TRUSTED_ORIGINS = [
#     "https://admin.hackudc.gpul.org",
# ]

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "es-es"

TIME_ZONE = "Europe/Madrid"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"
# STATIC_ROOT = BASE_DIR / "staticfiles"
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
EMAIL_HOST = "localhost"
EMAIL_PORT = 8025

# DEFAULT_FROM_EMAIL = ("no-reply@gpul.org",)
DEFAULT_FROM_EMAIL = "no-reply@gpul.org"
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
