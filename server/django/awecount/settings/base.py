import datetime
import os

import dj_database_url
from corsheaders.defaults import default_headers
from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

######################################################################
# Load environment variables from .env file
######################################################################

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv(dotenv_path=os.path.normpath(os.path.join(ROOT_DIR, ".env")))


######################################################################
# General
######################################################################
SECRET_KEY = os.environ.get("SECRET_KEY", get_random_secret_key())

DEBUG = os.environ.get("DEBUG", False) == "True"

ROOT_URLCONF = "awecount.urls"
APPEND_SLASH = True

WSGI_APPLICATION = "awecount.wsgi.application"
ASGI_APPLICATION = "awecount.asgi.application"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


######################################################################
# Domains
######################################################################
APP_URL = os.environ.get("APP_URL", "http://localhost:3000")

# TODO: Parse domain from APP_URL
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [*default_headers, "X-Session-Token"]

CORS_ORIGIN_WHITELIST = os.environ.get("CORS_ORIGIN_WHITELIST", "").split(",")
CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")


######################################################################
# Apps
######################################################################
INSTALLED_APPS = [
    # Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Inhouse apps
    "apps.users",
    "apps.company",
    "apps.authentication",
    "apps.aggregator",
    "apps.api",
    "apps.bank",
    "apps.ledger",
    "apps.product",
    "apps.tax",
    "apps.voucher",
    # 3rd party apps
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.mfa",
    "allauth.headless",
    "allauth.usersessions",
    "rest_framework",
    "corsheaders",
    "import_export",
    "django_filters",
    "djoser",
    "auditlog",
    "mptt",
    "django_q",
    "dbbackup",
]


######################################################################
# Middleware
######################################################################
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "apps.company.middleware.CompanyMiddleware",
]


######################################################################
# Templates
######################################################################
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.normpath(os.path.join(ROOT_DIR, "templates")),
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


######################################################################
# Databases
######################################################################
if bool(os.environ.get("DATABASE_URL")):
    # Parse database configuration from $DATABASE_URL
    DATABASES = {
        "default": dj_database_url.config(),
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DATABASE", "awecount-db"),
            "USER": os.environ.get("POSTGRES_USER", "postgres"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "postgres"),
            "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    }


######################################################################
# Caches
######################################################################
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}


######################################################################
# Storage
######################################################################
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {
            "location": os.path.normpath(os.path.join(ROOT_DIR, "media")),
        },
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}


######################################################################
# Sessions
######################################################################
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"


######################################################################
# Authentication
######################################################################
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

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

AUTH_USER_MODEL = "users.User"


######################################################################
# Localization
######################################################################
LANGUAGE_CODE = "en-us"

USE_TZ = True
TIME_ZONE = "Asia/Kathmandu"

USE_I18N = True
USE_L10N = True


######################################################################
# Static
######################################################################
STATIC_URL = "/static/"

STATICFILES_DIRS = [os.path.normpath(os.path.join(ROOT_DIR, "staticfiles"))]

STATIC_ROOT = os.path.normpath(os.path.join(ROOT_DIR, "static"))

MEDIA_ROOT = os.path.normpath(os.path.join(ROOT_DIR, "media"))

MEDIA_URL = "/media/"


############################################################################
# Debug toolbar
############################################################################
DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": lambda request: DEBUG}

if DEBUG:
    try:
        import debug_toolbar  # noqa F401

        INSTALLED_APPS += ["debug_toolbar"]
        MIDDLEWARE.insert(1, "debug_toolbar.middleware.DebugToolbarMiddleware")
    except ImportError:
        pass


######################################################################
# Sentry
######################################################################
if SENTRY_DSN := os.environ.get("SENTRY_DSN", None):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=os.environ.get("SENTRY_ENVIRONMENT"),
        integrations=[DjangoIntegration(), RedisIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True,
    )


######################################################################
# DRF
######################################################################
REST_FRAMEWORK = {
    "PAGE_SIZE": 20,
    "DEFAULT_PAGINATION_CLASS": "awecount.libs.pagination.PageNumberPagination",
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "apps.api.authentication.APIKeyAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "EXCEPTION_HANDLER": "awecount.libs.exception.exception_handler",
}

######################################################################
# Allauth & Simple JWT
######################################################################
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_USER_MODEL_USERNAME_FIELD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"

ACCOUNT_ADAPTER = "apps.authentication.adapters.AllAuthAccountAdapter"
HEADLESS_ADAPTER = "apps.authentication.adapters.AllAuthHeadlessAdapter"
HEADLESS_TOKEN_STRATEGY = "apps.authentication.strategies.SessionAndAccessTokenStrategy"
SOCIALACCOUNT_ADAPTER = "apps.authentication.adapters.AllAuthSocialAccountAdapter"

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
            "secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
        },
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
        "EMAIL_AUTHENTICATION": True,
    },
}

HEADLESS_ONLY = True
HEADLESS_FRONTEND_URLS = {
    "account_confirm_email": APP_URL + "/auth/verify-email/{key}/",
    "account_reset_password": APP_URL + "/auth/password/reset/",
    "account_reset_password_from_key": APP_URL + "/auth/password/reset/{key}/",
    "account_signup": APP_URL + "/auth/signup/",
    "socialaccount_login_error": APP_URL + "/auth/login/",
    "socialaccount_callback": APP_URL + "/auth/{provider}/callback/",
}

SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ("JWT", "Token"),
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(days=5),
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(days=7),
}


######################################################################
# Email
######################################################################
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
SERVER_EMAIL = os.environ.get("SERVER_EMAIL")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")

EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_PORT = os.environ.get("EMAIL_PORT")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", False)
EMAIL_USE_SSL = os.environ.get("EMAIL_USE_SSL", False)
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")


######################################################################
# Django Q2
######################################################################
Q_CLUSTER = {
    "retry": 60,
    "timeout": 30,
    "compress": True,
    "save_limit": 250,
    "queue_limit": 500,
    "cpu_affinity": 1,
    "django_redis": "default",
}

if SENTRY_DSN := os.environ.get("SENTRY_DSN", None):
    Q_CLUSTER["error_reporter"] = {"sentry": {"dsn": SENTRY_DSN}}


######################################################################
# DB Backup
######################################################################
DBBACKUP_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
DBBACKUP_FILENAME_TEMPLATE = "{databasename}-{servername}-{datetime}.{extension}"

DBBACKUP_STORAGE_OPTIONS = {
    "default_acl": "private",
    "access_key": os.environ.get("DBBACKUP_STORAGE_ACCESS_KEY"),
    "secret_key": os.environ.get("DBBACKUP_STORAGE_SECRET_KEY"),
    "bucket_name": os.environ.get("DBBACKUP_STORAGE_BUCKET_NAME", "db-backup"),
    "endpoint_url": os.environ.get("DBBACKUP_STORAGE_ENDPOINT_URL"),
    "location": os.environ.get("DBBACKUP_STORAGE_LOCATION", "db-backup"),
}


######################################################################
# Miscelleneous
######################################################################
POS_ITEMS_SIZE = 30
MPTT_ADMIN_LEVEL_INDENT = 20
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
