import os
from pathlib import Path
from urllib.parse import unquote, urlparse

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Carga variables desde archivo .env si existe en la raíz
load_dotenv(BASE_DIR / ".env")

# -----------------------------------------------------------------------------
# SEGURIDAD Y ENTORNO (PROHIBIDO DATOS QUEMADOS)
# -----------------------------------------------------------------------------
DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() in ("true", "1", "yes")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY") or os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise ImproperlyConfigured(
        "La variable de entorno DJANGO_SECRET_KEY o SECRET_KEY no está definida. "
        "Para producción es estrictamente obligatorio definir una clave secreta segura."
    )

# Hosts permitidos
raw_allowed_hosts = os.environ.get("ALLOWED_HOSTS", "")
if raw_allowed_hosts:
    ALLOWED_HOSTS = [h.strip() for h in raw_allowed_hosts.split(",") if h.strip()]
elif DEBUG:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "testserver"]
else:
    raise ImproperlyConfigured(
        "La variable de entorno ALLOWED_HOSTS no está definida. "
        "En producción debes especificar los dominios permitidos separados por comas (ej: midominio.com,api.midominio.com)."
    )

# Orígenes confiables para protección CSRF (crucial en producción HTTPS)
raw_csrf_origins = os.environ.get("CSRF_TRUSTED_ORIGINS", "")
if raw_csrf_origins:
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in raw_csrf_origins.split(",") if o.strip()]
else:
    CSRF_TRUSTED_ORIGINS = []

# -----------------------------------------------------------------------------
# APLICACIONES Y MIDDLEWARE
# -----------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "control.apps.ControlConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Servicio eficiente de estáticos en producción
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "familyflow.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "familyflow.wsgi.application"
ASGI_APPLICATION = "familyflow.asgi.application"

# -----------------------------------------------------------------------------
# BASE DE DATOS: EXCLUSIVAMENTE POSTGRESQL (CERO SQLITE / CERO DATOS QUEMADOS)
# -----------------------------------------------------------------------------
def parse_database_url(url: str) -> dict:
    parsed = urlparse(url)
    if parsed.scheme not in ("postgres", "postgresql"):
        raise ImproperlyConfigured(
            f"Esquema de base de datos no soportado: '{parsed.scheme}'. Debe ser postgresql:// o postgres://"
        )
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": unquote(parsed.path.lstrip("/")),
        "USER": unquote(parsed.username or ""),
        "PASSWORD": unquote(parsed.password or ""),
        "HOST": parsed.hostname or "",
        "PORT": str(parsed.port or 5432),
        "CONN_MAX_AGE": int(os.environ.get("DB_CONN_MAX_AGE", "600")),
    }


database_url = os.environ.get("DATABASE_URL")
db_name = os.environ.get("DB_NAME") or os.environ.get("POSTGRES_DB")

if database_url:
    DATABASES = {"default": parse_database_url(database_url)}
elif db_name:
    db_user = os.environ.get("DB_USER") or os.environ.get("POSTGRES_USER")
    db_password = os.environ.get("DB_PASSWORD") or os.environ.get("POSTGRES_PASSWORD")
    db_host = os.environ.get("DB_HOST") or os.environ.get("POSTGRES_HOST")
    db_port = os.environ.get("DB_PORT") or os.environ.get("POSTGRES_PORT", "5432")

    if not db_user or not db_host:
        raise ImproperlyConfigured(
            "Faltan variables para la conexión a PostgreSQL. "
            "Debes definir al menos DB_NAME, DB_USER, DB_PASSWORD y DB_HOST (o usar DATABASE_URL)."
        )

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": db_name,
            "USER": db_user,
            "PASSWORD": db_password or "",
            "HOST": db_host,
            "PORT": str(db_port),
            "CONN_MAX_AGE": int(os.environ.get("DB_CONN_MAX_AGE", "600")),
        }
    }
else:
    raise ImproperlyConfigured(
        "No se encontró configuración para la base de datos PostgreSQL.\n"
        "Debes definir la variable de entorno DATABASE_URL (ej: postgresql://usuario:clave@host:5432/nombre_db)\n"
        "o las variables individuales: DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT.\n"
        "SQLite ha sido eliminado por completo del proyecto."
    )

# -----------------------------------------------------------------------------
# VALIDACIÓN DE CONTRASEÑAS
# -----------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -----------------------------------------------------------------------------
# INTERNACIONALIZACIÓN Y ZONA HORARIA
# -----------------------------------------------------------------------------
LANGUAGE_CODE = os.environ.get("LANGUAGE_CODE", "es")
TIME_ZONE = os.environ.get("TIME_ZONE", "America/Bogota")
USE_I18N = True
USE_TZ = True

# -----------------------------------------------------------------------------
# ARCHIVOS ESTÁTICOS (PRODUCCIÓN CON WHITENOISE)
# -----------------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# -----------------------------------------------------------------------------
# PARÁMETROS DE SEGURIDAD PARA PRODUCCIÓN (HTTPS / CABECERAS)
# -----------------------------------------------------------------------------
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "True").lower() == "true"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "True").lower() == "true"
    CSRF_COOKIE_SECURE = os.environ.get("CSRF_COOKIE_SECURE", "True").lower() == "true"
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

    hsts_seconds = int(os.environ.get("SECURE_HSTS_SECONDS", "31536000"))
    if hsts_seconds > 0:
        SECURE_HSTS_SECONDS = hsts_seconds
        SECURE_HSTS_INCLUDE_SUBDOMAINS = True
        SECURE_HSTS_PRELOAD = True

# -----------------------------------------------------------------------------
# RUTAS DE AUTENTICACIÓN
# -----------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "control:login"
LOGIN_REDIRECT_URL = "control:dashboard"
LOGOUT_REDIRECT_URL = "control:login"
