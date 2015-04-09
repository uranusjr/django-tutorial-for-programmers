from .base import *     # noqa
import dj_database_url

DEBUG = False

SECRET_KEY = get_env_var('DJANGO_SECRET_KEY')

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

STATIC_ROOT = 'static'

DATABASES = {
    'default': dj_database_url.config()
}

ALLOWED_HOSTS = ['*']
