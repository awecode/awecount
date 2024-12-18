import os

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import MIDDLEWARE, REST_FRAMEWORK

SECRET_KEY = "secret"

DEBUG = False

MIDDLEWARE += [
    "whitenoise.middleware.WhiteNoiseMiddleware",
]
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        # 'logfile': {
        #     'class': 'logging.FileHandler',
        #     'filename': os.path.join(BASE_DIR, '..', 'logs', 'debug.log')
        # },
        # "mail_admins": {
        #     "level": "ERROR",
        #     "class": "django.utils.log.AdminEmailHandler",
        #     "include_html": True,
        # },
        "null": {
            "level": "DEBUG",
            "class": "logging.NullHandler",
        },
        # 'console': {
        #     'level': 'DEBUG',
        #     'class': 'logging.StreamHandler',
        #     'formatter': 'standard'
        # }
    },
    "loggers": {
        # "django": {
        #     "handlers": ["mail_admins", "console"],
        #     "level": "ERROR",
        #     "propagate": False,
        # },
        "django.security.DisallowedHost": {
            "handlers": ["null"],
            "propagate": False,
        },
        # "django.request": {
        #     "handlers": ["console"],
        #     "level": "INFO",
        #     "propagate": True,
        # },
        # "django.server": {
        #     "handlers": ["console"],
        #     "level": "DEBUG",
        #     "propagate": True,
        # },
    },
}

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

ALLOWED_HOSTS = ["billing.awecode.com", "be.awecountant.com"]

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = ("rest_framework.renderers.JSONRenderer",)

# SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("PGDATABASE", "billing"),
        "USER": os.environ.get("PGUSER", "postgres"),
        "PASSWORD": os.environ.get("PGPASSWORD", ""),
        "HOST": os.environ.get("PGHOST", ""),
        "PORT": os.environ.get("PGPORT", ""),
        "ATOMIC_REQUESTS": True,
    }
}

SERVER_EMAIL = "awecode.com <awecount+admin@awecode.com>"
DEFAULT_FROM_EMAIL = SERVER_EMAIL
EMAIL_BACKEND = "django_ses.SESBackend"
AWS_SES_REGION_NAME = "us-east-1"
AWS_SES_REGION_ENDPOINT = "email.us-east-1.amazonaws.com"
AWS_SES_ACCESS_KEY_ID = os.environ.get("AWS_SES_ACCESS_KEY_ID", "")
AWS_SES_SECRET_ACCESS_KEY = os.environ.get("AWS_SES_SECRET_ACCESS_KEY", "")

ADMINS = (
    ("Dipesh Acharya", "awecount+admin@awecode.com"),
)

CORS_ORIGIN_WHITELIST = (
    "https://awecountant.com",
    
)

BASE_URL = "https://awecountant.com/"

URL = "https://awecount.com"
MAX_FILE_UPLOAD_SIZE = 1024 * 1024
MAX_DEFAULT_EMAIL_ATTACHMENTS = 5
MAX_EMAIL_ATTACHMENTS = 8
MAX_IMPORT_FILE_SIZE = 1024 * 1024 * 20

EMAIL_SUBJECT_PREFIX = "[AWECOUNTING] "

sentry_sdk.init(
    dsn="",
    integrations=[DjangoIntegration()],
    enable_tracing=True,
    traces_sample_rate=0.1,
    send_default_pii=True,
    environment="Production",
)
