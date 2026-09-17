"""Base settings shared across all environments.

Environment-specific settings live in ``dev.py`` and ``prod.py``, which
import everything from this module and override as needed. Secrets and
environment-dependent values are read from environment variables via
``django-environ``; never hardcode secrets here.
"""

from pathlib import Path

import environ
from django.contrib.messages import constants as message_constants

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# BASE_DIR points at the repository root (three levels up from this file:
# config/settings/base.py -> config/settings -> config -> repo root).
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
env = environ.Env(
    DEBUG=(bool, False),
)

# Read a .env file at the repo root if present. In production, real
# environment variables take precedence and a .env file may be absent.
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="insecure-dev-key-change-me")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "django_filters",
]

# Local domain apps. Ordering follows the documented build sequence.
LOCAL_APPS = [
    "apps.common",
    "apps.accounts",
    "apps.dashboard",
    "apps.catalog",
    "apps.inventory",
    "apps.purchasing",
    "apps.sales",
    "apps.reporting",
    "apps.audit",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Site-wide authentication + inactive-user lockout (after auth middleware).
    "apps.accounts.middleware.LoginRequiredMiddleware",
    "apps.accounts.middleware.ActiveUserMiddleware",
]

# Routes reachable without authentication. Everything else requires login via
# LoginRequiredMiddleware. Per-view permission checks apply on top of this.
LOGIN_EXEMPT_URL_NAMES = [
    "accounts:login",
    "accounts:logout",
    "accounts:password_reset",
    "accounts:password_reset_done",
    "accounts:password_reset_confirm",
    "accounts:password_reset_complete",
]
LOGIN_EXEMPT_PREFIXES = [
    "/static/",
    "/media/",
    # Django admin has its own authentication flow.
    "/admin/",
]

ROOT_URLCONF = "config.urls"

# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------
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
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------------------
# Database (PostgreSQL via DATABASE_URL, parsed by django-environ)
# ---------------------------------------------------------------------------
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgres://ims_user:change_me_locally@localhost:5432/ims",
    ),
}
# Reuse connections for 60s to reduce per-request connection overhead.
DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
# Custom user model is introduced in Phase 2 (apps.accounts). Declared here so
# the reference is stable from the start; the migration arrives with the model.
AUTH_USER_MODEL = "accounts.User"

# Authenticate inactive users too, so the login form can distinguish "wrong
# credentials" from "correct credentials, but account disabled" and show the
# right message (App Flow §3). The form's confirm_login_allowed() then rejects
# inactive users, and ActiveUserMiddleware blocks any authenticated-but-
# inactive session.
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.AllowAllUsersModelBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation."
        "UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation."
        "MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation."
        "CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation."
        "NumericPasswordValidator",
    },
]

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "dashboard:index"
LOGOUT_REDIRECT_URL = "accounts:login"

# ---------------------------------------------------------------------------
# Internationalization / time
# ---------------------------------------------------------------------------
LANGUAGE_CODE = env("LANGUAGE_CODE", default="en-us")
TIME_ZONE = env("TIME_ZONE", default="UTC")
USE_I18N = True
USE_TZ = True  # Store datetimes in UTC; display in local timezone.

# ---------------------------------------------------------------------------
# Static & media
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default storages. The staticfiles backend here is the plain one, which works
# in development without a collectstatic manifest. Production overrides the
# staticfiles backend with WhiteNoise's compressed+hashed manifest storage
# (see prod.py), which requires collectstatic to have run.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Upload limits (Tech Stack: 5 MB max image upload).
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]

# ---------------------------------------------------------------------------
# Messages -> Tailwind-friendly tags (used by the toast component later)
# ---------------------------------------------------------------------------

MESSAGE_TAGS = {
    message_constants.DEBUG: "debug",
    message_constants.INFO: "info",
    message_constants.SUCCESS: "success",
    message_constants.WARNING: "warning",
    message_constants.ERROR: "error",
}

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
# Separate rotating log files for application, errors, security, and audit
# concerns, as required by the Tech Stack. The logs/ directory is created at
# import time so logging never fails on a fresh checkout.
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)


def _rotating_file(filename: str, level: str) -> dict:
    """Build a rotating file handler config (5 MB x 5 backups)."""
    return {
        "level": level,
        "class": "logging.handlers.RotatingFileHandler",
        "filename": LOG_DIR / filename,
        "maxBytes": 5 * 1024 * 1024,
        "backupCount": 5,
        "formatter": "verbose",
    }


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} [{levelname}] {name}: {message}",
            "style": "{",
        },
        "simple": {
            "format": "[{levelname}] {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "app_file": _rotating_file("application.log", "INFO"),
        "error_file": _rotating_file("errors.log", "ERROR"),
        "security_file": _rotating_file("security.log", "INFO"),
        "audit_file": _rotating_file("audit.log", "INFO"),
    },
    "root": {
        "handlers": ["console", "app_file"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "app_file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["security_file", "console"],
            "level": "INFO",
            "propagate": False,
        },
        # Application-owned loggers (used by services from Phase 2 onward).
        "ims": {
            "handlers": ["console", "app_file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        "ims.audit": {
            "handlers": ["audit_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
