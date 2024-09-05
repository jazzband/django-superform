import warnings
warnings.simplefilter('always')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

USE_I18N = True

INSTALLED_APPS = [
    'django_superform',
    'tests',
]

MIDDLEWARE_CLASSES = ()

STATIC_URL = '/static/'

SECRET_KEY = '0'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['tests/templates', 'django-superform/templates'],
        'APP_DIRS': True
    }
]

USE_TZ = False
