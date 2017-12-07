import os

from .base import BASE_DIR
from .base import *     # noqa

SECRET_KEY = 'a!e(mpno%t%^os=+e@&tl+%w-@xw$)7mgy!(cv@03_7t=mvi3#'

DEBUG = True


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.dirname(BASE_DIR), 'db.sqlite3'),
    }
}
