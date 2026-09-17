"""Development settings.

Local development defaults: DEBUG on, permissive hosts, console email, and
relaxed security cookies (never used in production).
"""

from .base import *  # noqa: F401,F403
from .base import env

DEBUG = env.bool("DEBUG", default=True)

ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "0.0.0.0"]
)

# Email goes to the console in development (used by password reset in Phase 2).
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Insecure cookies are acceptable locally over plain HTTP.
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# django-debug-toolbar is intentionally omitted (not in the approved stack).
