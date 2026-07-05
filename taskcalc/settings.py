"""
Configuración de Django para el proyecto Task & Calc.

Toda la configuración sensible se lee desde variables de entorno (.env)
usando django-environ, y la base de datos con dj-database-url
(compatible con Supabase / PostgreSQL).
"""

from pathlib import Path

import dj_database_url
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------------------------------------------
# Variables de entorno
# ------------------------------------------------------------------
env = environ.Env(
    DEBUG=(bool, False),
    FEATURE_CALCULATOR=(bool, False),
)

# Lee el archivo .env si existe (en producción se usan las env vars del host)
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="django-insecure-solo-para-desarrollo")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# ------------------------------------------------------------------
# FEATURE FLAGS (Requisito de variabilidad)
#   FEATURE_CALCULATOR=False -> Versión 1: solo Sistema de Tareas
#   FEATURE_CALCULATOR=True  -> Versión 2: Tareas + Calculadora Técnica
# ------------------------------------------------------------------
FEATURE_CALCULATOR = env("FEATURE_CALCULATOR")

# ------------------------------------------------------------------
# Aplicaciones
# ------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Apps del proyecto
    "tasks",
    "calculator",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # estáticos en producción
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "taskcalc.urls"

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
                # Expone los feature flags a todos los templates
                "taskcalc.context_processors.feature_flags",
            ],
        },
    },
]

WSGI_APPLICATION = "taskcalc.wsgi.application"

# ------------------------------------------------------------------
# Base de datos: PostgreSQL (Supabase) vía DATABASE_URL.
# Si no está definida, cae a SQLite (solo para desarrollo local).
# ------------------------------------------------------------------
DATABASE_URL = env("DATABASE_URL", default="")
DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL or f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ------------------------------------------------------------------
# Validación de contraseñas (admin de Django)
# ------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ------------------------------------------------------------------
# Internacionalización
# ------------------------------------------------------------------
LANGUAGE_CODE = "es"
TIME_ZONE = "America/Lima"
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------------
# Archivos estáticos (CSS / JS) servidos con WhiteNoise en producción
# ------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ------------------------------------------------------------------
# Seguridad adicional en producción
# ------------------------------------------------------------------
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
