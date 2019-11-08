from .base import INSTALLED_APPS, MIDDLEWARE, REST_FRAMEWORK

DEBUG = True

SECRET_KEY = '4oiwq=^7+@ub=shgbo#=gj17jveh+_*9tuqfx5fa-1orav(7xx'

INSTALLED_APPS += ['debug_toolbar', 'django_extensions']

MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

INTERNAL_IPS = ['127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'awecount',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': '',
        'PORT': '',
    }
}
CORS_ORIGIN_WHITELIST = (
    'http://localhost:8080',
    'http://127.0.0.1:8080',
)

BASE_URL = 'http://localhost:8080/'