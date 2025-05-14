from .base import *


DEBUG = False

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

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/django/django.log'),
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/django/error.log'),
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'error_file', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['error_file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.template': {
            'handlers': ['error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'web': {
            'handlers': ['file', 'error_file', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Email settings for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'in-v3.mailjet.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = os.getenv('MAILJET_API_KEY')
EMAIL_HOST_PASSWORD = os.getenv('MAILJET_SECRET_KEY')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@djangogramm.com')

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_REFERRER_POLICY = 'same-origin'

# Production logging configuration
LOGGING['handlers']['mail_admins'] = {
    'level': 'ERROR',
    'class': 'django.utils.log.AdminEmailHandler',
    'formatter': 'verbose',
}

LOGGING['loggers']['django']['handlers'].append('mail_admins')
LOGGING['loggers']['web']['handlers'].append('mail_admins')

# Add specific loggers for production
LOGGING['loggers'].update({
    'django.request': {
        'handlers': ['error_file', 'mail_admins'],
        'level': 'ERROR',
        'propagate': False,
    },
    'django.server': {
        'handlers': ['error_file'],
        'level': 'ERROR',
        'propagate': False,
    },
    'django.template': {
        'handlers': ['error_file'],
        'level': 'ERROR',
        'propagate': False,
    },
    'django.db.backends': {
        'handlers': ['error_file'],
        'level': 'ERROR',
        'propagate': False,
    },
})

SESSION_COOKIE_AGE = 1209600 
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
