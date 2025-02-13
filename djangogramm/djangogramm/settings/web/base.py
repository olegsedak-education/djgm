import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api
import cloudinary_storage

load_dotenv(find_dotenv())

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DJANGO_SETTINGS_MODULE = os.environ.get('DJANGO_SETTINGS_MODULE')
MAX_IMAGE_SIZE = int(os.environ.get('MAX_IMAGE_SIZE', 1600))
THUMBNAIL_SIZE = int(os.environ.get('THUMBNAIL_SIZE', 200))
IMAGE_QUALITY = int(os.environ.get('IMAGE_QUALITY', 85))

TEMPLATE_DIR = BASE_DIR / os.environ.get("TEMPLATE_DIR", "templates")
MEDIA_DIR = BASE_DIR /os.environ.get("MEDIA_DIR", "media")
STATIC_DIR = BASE_DIR / os.environ.get("STATIC_DIR", "static")
STATIC_URL= os.environ.get("STATIC_URL","/static/")
MEDIA_URL = os.environ.get("MEDIA_URL", "/media/")
IMAGE_DIR = MEDIA_DIR / os.environ.get("IMAGE_DIR", "images")
DEFAULT_AVATAR_IMG_PATH = os.environ.get("DEFAULT_AVATAR_IMG_PATH", "media/default/unAuth.jpg")
STATICFILES_DIRS = [STATIC_DIR]
MEDIA_ROOT = MEDIA_DIR

# CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_KEY_NAME = os.environ.get('CLOUDINARY_KEY_NAME')
# CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
# CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
# CLOUDINARY_UPLOAD_PRESET = os.environ.get('CLOUDINARY_UPLOAD_PRESET')
# CLOUDINARY_URL=f'cloudinary://{CLOUDINARY_API_KEY}:{CLOUDINARY_API_SECRET}@{CLOUDINARY_CLOUD_NAME}'

cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
    'UPLOAD_PRESET': os.environ.get('CLOUDINARY_UPLOAD_PRESET'),
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
# STATICFILES_STORAGE = 'cloudinary_storage.storage.StaticHashedCloudinaryStorage'


SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = True

INTERNAL_IPS = ["localhost", "127.0.0.1", ]

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'cloudinary_storage',
    'cloudinary',
    "django_extensions",
    # "easy_thumbnails",
    "crispy_forms",
    "crispy_bootstrap5",
    "web",
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

AUTH_USER_MODEL = "web.AppUser"

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",

    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "djangogramm.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATE_DIR],
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

WSGI_APPLICATION = "djangogramm.wsgi.application"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}

# THUMBNAIL_ALIASES = {
#     '': {
#         'avatar': {'size': (50, 50), 'crop': True},
#         'thumbnail': {'size': (200, 200), 'crop': True},
#         'default': {'size': (1600, 1600), 'crop': True},
#     },
# }

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

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Kiev"

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
