from .base import INSTALLED_APPS, MIDDLEWARE, REST_FRAMEWORK

DEBUG = True

SECRET_KEY = "4oiwq=^7+@ub=shgbo#=gj17jveh+_*9tuqfx5fa-1orav(7xx"

INSTALLED_APPS += ["debug_toolbar", "django_extensions"]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] += [
    "rest_framework.authentication.SessionAuthentication"
]

INTERNAL_IPS = ["127.0.0.1"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "awecount",
        "USER": "postgres",
        "PASSWORD": "password",
        "HOST": "",
        "PORT": "",
    }
}
CORS_ORIGIN_WHITELIST = (
    "http://localhost:8080",
    "http://localhost:8081",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:9000",
    "http://localhost:9000",
)

CSRF_TRUSTED_ORIGINS = (
    "http://localhost:8080",
    "http://localhost:8081",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:9000",
    "http://localhost:9000",
)

CORS_ALLOWED_ORIGINS = (
    "http://localhost:8080",
    "http://localhost:8081",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:9000",
    "http://localhost:9000",
)

BASE_URL = "http://localhost:8080/"

# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     'formatters': {
#         'standard': {
#             'format': "[%(asctime)s] %(levelname)s %(message)s",
#             'datefmt': "%d/%b/%Y %H:%M:%S"
#         }
#     },
#     "handlers": {
#         "file": {
#             "level": "DEBUG",
#             "class": "logging.FileHandler",
#             "filename": "./debug.log",
#             'formatter': 'standard'
#         },
#     },
#     "loggers": {
#         "django": {
#             "handlers": ["file"],
#             "level": "INFO",
#             "propagate": True,
#             'formatter': 'standard'
#         },
#     },
# }

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
BANK_RECONCILIATION_TOLERANCE = 0.01
BANK_RECONCILIATION_STATEMENT_LOOKBACK_DAYS = 3
BANK_RECONCILIATION_STATEMENT_LOOKAHEAD_DAYS= 3
