import datetime
import os
from pathlib import Path

import dj_database_url
from corsheaders.defaults import default_headers
from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

######################################################################
# Load environment variables from .env file
######################################################################


BASE_DIR = Path(__file__).resolve().parent.parent

ROOT_DIR = BASE_DIR.parent

PROJECT_DIR = ROOT_DIR.parent.parent

load_dotenv(dotenv_path=PROJECT_DIR / ".env")


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
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

APP_URL = os.environ.get("APP_URL", "http://localhost:3000")


CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [*default_headers, "X-Session-Token", "X-Invitation-Token"]

CORS_ORIGIN_WHITELIST = os.environ.get("CORS_ORIGIN_WHITELIST", APP_URL).split(",")
CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS", APP_URL).split(",")

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
    # Project apps
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
            "NAME": os.environ.get("POSTGRES_DATABASE", "awecount"),
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
            "location": os.environ.get("MEDIA_ROOT", ROOT_DIR / "media"),
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
# Static & Media
######################################################################
STATIC_URL = os.environ.get("STATIC_URL", "/static/")
STATIC_ROOT = os.environ.get("STATIC_ROOT", ROOT_DIR / "static")
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = os.environ.get("MEDIA_URL", "/media/")
MEDIA_ROOT = os.environ.get("MEDIA_ROOT", ROOT_DIR / "media")


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
        enable_tracing=True,
        traces_sample_rate=1.0,
        send_default_pii=True,
    )

    MIDDLEWARE.insert(-1, "lib.sentry.middleware.SentryMiddleware")


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
SIGNUP_ALLOWED = os.environ.get("SIGNUP_ALLOWED", "True") == "True"

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
EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"
    if not DEBUG
    else "django.core.mail.backends.console.EmailBackend"
)

SERVER_EMAIL = os.environ.get("SERVER_EMAIL")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")

EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_PORT = os.environ.get("EMAIL_PORT")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS") == "True"
EMAIL_USE_SSL = os.environ.get("EMAIL_USE_SSL") == "True"
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


################################################################
# Whitenoise
################################################################
if os.environ.get("USE_WHITENOISE", "False") == "True":
    MIDDLEWARE.insert(2, "whitenoise.middleware.WhiteNoiseMiddleware")
    STORAGES["staticfiles"] = {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    }


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

DBBACKUP_FILENAME_TEMPLATE = "{databasename}-{servername}-{datetime}.{extension}"
DBBACKUP_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"


######################################################################
# Miscelleneous
######################################################################
POS_ITEMS_SIZE = 30
MPTT_ADMIN_LEVEL_INDENT = 20
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

ACCOUNT_SYSTEM_CODES = {
    "Cash": "CASH",
    "Sales Account": "SALES",
    "Discount Income": "DIS-INCOME",
    "Purchase Account": "PURCHASE",
    "Expiry Expense": "EXP-EXP",
    "Opening Balance Difference": "OPEN-BAL-DIFF",
    "Profit and Loss Account": "PL",
    "Discount Expenses": "DIS-EXP",
    "Damage Expense": "DAM-EXP",
    "TDS Receivables": "TDS-REC",
}

ACCOUNT_CATEGORY_SYSTEM_CODES = {
    "Bank Accounts": "BANK",
    "Customers": "CUST",
    "Suppliers": "SUPP",
    "Bank Charges": "BANK-CHG",
    "Fixed Assets": "FIX-ASSET",
    "Tax Receivables": "TAX-REC",
    "Cash Accounts": "CASH-ACCOUNTS",
    "Duties & Taxes": "DUT-TAX",
    "Sales": "SALES",
    "Purchase": "PURCHASE",
    "Direct Expenses": "DIR-EXP",
    "Indirect Expenses": "IND-EXP",
    "Discount Expenses": "DIS-EXP",
    "Discount Income": "DIS-INCOME",
    "Income": "INCOME",
    "Expenses": "EXPENSES",
}

# Bank reconciliation settings
BANK_RECONCILIATION_TOLERANCE = 0.01
BANK_RECONCILIATION_ADJUSTMENT_THRESHOLD = 1
BANK_RECONCILIATION_STATEMENT_LOOKBACK_DAYS = 3
BANK_RECONCILIATION_STATEMENT_LOOKAHEAD_DAYS = 3

# File upload settings
MAX_FILE_UPLOAD_SIZE = 1024 * 1024
MAX_IMPORT_FILE_SIZE = 1024 * 1024 * 20

# Email attachment settings
MAX_EMAIL_ATTACHMENTS = 8
MAX_DEFAULT_EMAIL_ATTACHMENTS = 5
