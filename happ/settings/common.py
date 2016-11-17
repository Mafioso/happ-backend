"""
Django settings for happ project.

Generated by 'django-admin startproject' using Django 1.10.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
import datetime

from django.utils.translation import ugettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(e2%9phpj5%2z6z-i*20cj&f@1x#1l=ofn_v=k5rq*hs9^6fk#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['happ.westeurope.cloudapp.azure.com', 'happ.dev']


# Application definition

INSTALLED_APPS = [
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    # 'django.contrib.sessions',
    # 'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_mongoengine',
    'djcelery',
    'anymail',
    'happ',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'happ.auth.middleware.UserMiddleware',
]

ROOT_URLCONF = 'happ.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'happ.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # }
}

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'
MEDIA_URL = '/uploads/'
MEDIA_URL_NO_TRAILING_SLASH = '/uploads'
MEDIA_ROOT = '/uploads'
PAGE_SIZE = 10

NGINX_UPLOAD_ROOT = os.path.join(MEDIA_ROOT, 'media')
NGINX_AVATAR_ROOT = os.path.join(MEDIA_ROOT, 'avatars')
NGINX_MISC_ROOT = os.path.join(MEDIA_ROOT, 'misc')
NGINX_TMP_UPLOAD_ROOT = os.path.join(MEDIA_ROOT, 'tmp')

MONGODB_PORT = 27017
MONGODB_HOST_NAME = os.getenv('MONGO_PORT_27017_TCP_ADDR', '127.0.0.1')
MONGODB_HOST = 'mongodb://{host}:{port}'.format(host=MONGODB_HOST_NAME, port=MONGODB_PORT)
MONGODB_NAME = 'happ1'

REST_FRAMEWORK = {
    'UNAUTHENTICATED_USER': None, # temp
    'PAGE_SIZE': PAGE_SIZE,
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.TemplateHTMLRenderer',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'happ.auth.authentication.CookieJSONWebTokenAuthentication',
    ),
}

JWT_AUTH = {
    'JWT_PAYLOAD_HANDLER': 'happ.utils.jwt_payload_handler',
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=365),
    'JWT_ALLOW_REFRESH': True,
}

LOGIN_URL = 'admin-login'

AUTHENTICATION_BACKENDS = ('happ.auth.backends.HappAuthBackend', )

DEFAULT_FROM_EMAIL = 'askhat.omarov91@gmail.com'

ADMINS = [
    ('Askhat', 'askhat.omarov91@gmail.com'),
]

ANYMAIL = {
    "MAILGUN_API_KEY": "key-a966a5efd94d4ee543331d9109e69d95",
    "MAILGUN_SENDER_DOMAIN": 'sandbox7d7d8f136a6c447084ee631344625956.mailgun.org',
}

EMAIL_BACKEND = "anymail.backends.mailgun.MailgunBackend"

HAPP_LANGUAGES_VERBOSE = [
    {'code': 'en', 'text': _('English'), },
    {'code': 'ru', 'text': _('Russian'), },
    {'code': 'fr', 'text': _('French'), },
    {'code': 'it', 'text': _('Italian'), },
    {'code': 'es', 'text': _('Spanish'), },
    {'code': 'de', 'text': _('German'), },
]

HAPP_LANGUAGES = map(lambda x: x['code'], HAPP_LANGUAGES_VERBOSE)

DATE_STRING_FIELD_FORMAT = "%Y%m%d"
TIME_STRING_FIELD_FORMAT = "%H%M%S"

GOOGLE_API_KEY = 'AIzaSyBXnpQ8pPpfLsud5qqE6-YYhVW_DsR8Ce4'
GOOGLE_TRANSLATE_LINK = 'https://www.googleapis.com/language/translate/v2?key={}&q={}&target={}'
GOOGLE_URL_SHORTENER_LINK = 'https://www.googleapis.com/urlshortener/v1/url?key={}'

BROKER_USER_PASSWORD = os.getenv('RABBITMQ_ENV_RABBITMQ_USER_PASSWD', 'guest:guest')
# BROKER_VHOST = os.getenv('RABBITMQ_ENV_RABBITMQ_DEFAULT_VHOST', '/')

BROKER_URL = 'amqp://{user_passwd}@{host}/{vhost}'.format(**{
    'user_passwd': BROKER_USER_PASSWORD,
    'host': os.getenv('RABBITMQ_PORT_5672_TCP_ADDR', '127.0.0.1'),
    'port': os.getenv('RABBITMQ_PORT_5672_TCP_PORT', 5672),
    'vhost': os.getenv('RABBITMQ_ENV_RABBITMQ_DEFAULT_VHOST', '/')
})
