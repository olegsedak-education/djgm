from .base import *


DEBUG = True

ALLOWED_HOSTS = ['*']

SHARE_URL = "http://127.0.0.1:8000"

LOCAL_INSTALLED_APPS = [
    "debug_toolbar"
]

INSTALLED_APPS = INSTALLED_APPS + LOCAL_INSTALLED_APPS


DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': 'db.sqlite3',
}
