import os

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
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "include_html": True,
        },
        "null": {
            "level": "DEBUG",
            "class": "logging.NullHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.security.DisallowedHost": {
            "handlers": ["null"],
            "propagate": False,
        },
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

ALLOWED_HOSTS = [
    "billing.awecode.com",
    "be.awecountant.com",
    "awecounting-backend-production.up.railway.app",
    "awecountant-be-global-production.up.railway.app",
    "bedemo.awecountant.com",
]

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
    "https://awecount.com",
    "capacitor://localhost",
    "https://localhost",
    "https://demo.awecountant.com",
)

BASE_URL = "https://awecountant.com/"

EMAIL_SUBJECT_PREFIX = "[AWECOUNTING-TEST] "
