"""
Django settings for the DressIT project.

Plateforme de vente de vêtements (Homme / Femme) avec gestion des commandes,
paiement, espace client, multilingue (FR / EN) et thème sombre / clair.
"""

import os
from pathlib import Path

from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
# En production, définissez la variable d'environnement DRESSIT_SECRET_KEY.
SECRET_KEY = os.environ.get(
    "DRESSIT_SECRET_KEY",
    "django-insecure--*z!j*q8f41fjl5w#y0#7xw7=1+4jgu16&75r6jg8i##@i85hn",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DRESSIT_DEBUG", "1") == "1"

ALLOWED_HOSTS = os.environ.get("DRESSIT_ALLOWED_HOSTS", "*").split(",")

CSRF_TRUSTED_ORIGINS = [
    o for o in os.environ.get("DRESSIT_CSRF_TRUSTED_ORIGINS", "").split(",") if o
]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "store",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",  # i18n : doit suivre SessionMiddleware
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "dressit.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "store.context_processors.store_globals",
            ],
        },
    },
]

WSGI_APPLICATION = "dressit.wsgi.application"


# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization — français par défaut, anglais disponible.
LANGUAGE_CODE = "fr"

LANGUAGES = [
    ("fr", _("Français")),
    ("en", _("English")),
]

LOCALE_PATHS = [BASE_DIR / "locale"]

TIME_ZONE = "UTC"

USE_I18N = True
USE_TZ = True


# Static & media files
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Authentification
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "account"
LOGOUT_REDIRECT_URL = "home"


# Devise de la boutique (symbole affiché à côté des prix)
DRESSIT_CURRENCY_SYMBOL = os.environ.get("DRESSIT_CURRENCY_SYMBOL", "€")

# Livraison : frais fixes, offerte au-delà d'un certain montant.
DRESSIT_SHIPPING_FEE = os.environ.get("DRESSIT_SHIPPING_FEE", "4.90")
DRESSIT_FREE_SHIPPING_THRESHOLD = os.environ.get("DRESSIT_FREE_SHIPPING_THRESHOLD", "50")

# E-mail : en développement, les messages s'affichent dans la console.
# En production, définissez EMAIL_BACKEND SMTP via les variables d'environnement.
EMAIL_BACKEND = os.environ.get(
    "DRESSIT_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.environ.get("DRESSIT_EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("DRESSIT_EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("DRESSIT_EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("DRESSIT_EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("DRESSIT_EMAIL_USE_TLS", "1") == "1"
DEFAULT_FROM_EMAIL = os.environ.get("DRESSIT_FROM_EMAIL", "DressIT <no-reply@dressit.local>")

# Messages : classes CSS compatibles avec notre thème
from django.contrib.messages import constants as message_constants  # noqa: E402

MESSAGE_TAGS = {
    message_constants.DEBUG: "debug",
    message_constants.INFO: "info",
    message_constants.SUCCESS: "success",
    message_constants.WARNING: "warning",
    message_constants.ERROR: "error",
}
