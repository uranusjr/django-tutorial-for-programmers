from .base import *     # noqa

SECRET_KEY = r'd*0()gv$rm*u&4noa6ehq^+9gsx7tpt$2qw^f%soj3%r5j18*l'

DEBUG = True

TEMPLATE_DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.dirname(BASE_DIR), 'db.sqlite3'),
    }
}
