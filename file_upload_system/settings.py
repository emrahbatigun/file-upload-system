"""
Django settings for file_upload_system project.

Generated by 'django-admin startproject' using Django 5.0.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path

import pymysql
import os
import environ

env = environ.Env()
environ.Env.read_env()

AWS_ACCESS_KEY = env("AWS_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
REGION_NAME = env("REGION_NAME")
BUCKET_NAME = env("BUCKET_NAME")
AWS_ENCRYPTION_TYPE = env("AWS_ENCRYPTION_TYPE")
AWS_ENCRYPTION_KEY_ID = env("AWS_ENCRYPTION_KEY_ID")

pymysql.install_as_MySQLdb()


# Enable security settings
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

DATA_UPLOAD_MAX_MEMORY_SIZE = 2048  # Set max upload size to 2KB

LOGIN_URL = '/signin/'
LOGIN_REDIRECT_URL = ''  # Redirect to 'home' after login
LOGOUT_REDIRECT_URL = 'signin'  # Redirect to sign-in page after logout

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False


SERVER_IP = env("SERVER_IP")

ALLOWED_HOSTS = [SERVER_IP]

ORIGIN_1 = "https://" + SERVER_IP
ORIGIN_2 = "http://" + SERVER_IP
CSRF_TRUSTED_ORIGINS = [ORIGIN_1,ORIGIN_2]

SESSION_COOKIE_SECURE = False # True when deployed to a domain
CSRF_COOKIE_SECURE = False # True when deployed to a domain
SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # DRF
    'rest_framework',
    # APPS
    'files.apps.FilesConfig',
    'users.apps.UsersConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]



ROOT_URLCONF = 'file_upload_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'builtins': [
                'django.templatetags.static',
                'file_upload_system.templatetags.app_tags',
            ]
        },
    },
]

WSGI_APPLICATION = 'file_upload_system.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
SSL_PATH = env("SSL_PATH")


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',       
        'NAME': env("DB_NAME"),
        'USER': env("DB_USER"),
        'PASSWORD': env("DB_PASSWORD"),
        'HOST': env("DB_HOST"),
        'PORT': env("DB_PORT"),
        'OPTIONS': {
            'ssl': {"ca": os.path.join(BASE_DIR, SSL_PATH)}  
        }
    }
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '10/minute',
    },
}


LOG_DIR = Path(BASE_DIR / 'logs')
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/django.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
}



# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LAYOUT_DIR = 'layout'
NAME = 'File Upload System'

LAYOUT_ASSETS = {
    "favicon": "media/logos/favicon.ico",
    "fonts": [
        'https://fonts.googleapis.com/css?family=Inter:300,400,500,600,700',
    ],
    "css": [
        "plugins/global/plugins.bundle.css",
        "css/style.bundle.css"
    ],
    "js": [
        "plugins/global/plugins.bundle.js",
        "js/scripts.bundle.js",
    ]
}

LAYOUT_VENDORS = {
    "datatables": {
        "css": [
            "plugins/custom/datatables/datatables.bundle.css"
        ],
        "js": [
            "plugins/custom/datatables/datatables.bundle.js"
        ]
    },
    "cookiealert": {
        "css": [
            "plugins/custom/cookiealert/cookiealert.bundle.css"
        ],
        "js": [
            "plugins/custom/cookiealert/cookiealert.bundle.js"
        ]
    },
    "vis-timeline": {
        "css": [
            "plugins/custom/vis-timeline/vis-timeline.bundle.css"
        ],
        "js": [
            "plugins/custom/vis-timeline/vis-timeline.bundle.js"
        ]
    },
    "bootstrap-select": {
        "css": [
            "plugins/custom/bootstrap-select/bootstrap-select.bundle.css"
        ],
        "js": [
            "plugins/custom/bootstrap-select/bootstrap-select.bundle.js"
        ]
    }
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
