from .base import *     # noqa

DEBUG = False

SECRET_KEY = get_env_var('DJANGO_LUNCH_SECRET_KEY')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'lunch',
        'USER': get_env_var('DJANGO_LUNCH_DATABASE_DEFAULT_USER'),
        'PASSWORD': get_env_var('DJANGO_LUNCH_DATABASE_DEFAULT_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '',
    },
}

ALLOWED_HOSTS = ['*']

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static')

MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'media')
