import os

from .base import BASE_DIR


DEBUG = True

SECRET_KEY = '4oiwq=^7+@ub=shgbo#=gj17jveh+_*9tuqfx5fa-1orav(7xx'

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

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