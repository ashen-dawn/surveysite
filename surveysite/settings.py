"""
Django settings for surveysite project.

Generated by 'django-admin startproject' using Django 3.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
from django.contrib.messages import constants as message_constants
import os
import datetime

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECURITY WARNING: don't run with debug turned on in production!
SECRET_KEY = os.environ.get('WEBSITE_SECRET')

REDDIT_OAUTH_SECRET = os.environ.get('WEBSITE_REDDIT_OAUTH_SECRET')
REDDIT_OAUTH_CLIENT_ID = os.environ.get('WEBSITE_REDDIT_OAUTH_CLIENT_ID')

DEBUG = True if os.environ.get('WEBSITE_DEBUG') else False

use_https = True if os.environ.get('WEBSITE_USE_HTTPS') else False

allowed_hosts_env = os.environ.get('WEBSITE_ALLOWED_HOSTS')
ALLOWED_HOSTS = allowed_hosts_env.split(';') if allowed_hosts_env else []
CSRF_TRUSTED_ORIGINS = [('https://' if use_https else 'http://') + host for host in ALLOWED_HOSTS]

SESSION_COOKIE_SECURE = use_https
CSRF_COOKIE_SECURE = use_https
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https' if use_https else 'http'


# This started becoming necessary after upgrading @vue/cli from v4 to v5?
if DEBUG:
    import mimetypes
    mimetypes.add_type('application/javascript', '.js', True)

# Application definition

INSTALLED_APPS = [
    'survey.apps.SurveyConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.reddit',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'htmlmin.middleware.HtmlMinifyMiddleware',
    
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'htmlmin.middleware.MarkRequestMiddleware',
]

ROOT_URLCONF = 'surveysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'frontend/dist/'], # Shitty way to make index.html usable as a template, will also make all of Vite's output files usable as templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Explicitly set the default type of primary fields of models to AutoField - in the future, Django will use BigAutoField by default
# https://docs.djangoproject.com/en/3.2/releases/3.2/#customizing-type-of-auto-created-primary-keys
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SOCIALACCOUNT_PROVIDERS = {
    'reddit': {
        'APP': {
            'client_id': REDDIT_OAUTH_CLIENT_ID,
            'secret': REDDIT_OAUTH_SECRET,
            'key': '',
        },
        'SCOPE': ['identity'],
        'USER_AGENT': 'django:animesurvey:1.0 (by /u/DragonsOnOurMountain)',
        'AUTH_PARAMS': {
            'duration': 'permanent',
        },
    }
}

ACCOUNT_ADAPTER = 'surveysite.adapters.CustomAccountAdapter'

MESSAGE_TAGS = {
    message_constants.DEBUG: 'primary',
    message_constants.INFO: 'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR: 'danger',
}
MESSAGE_LEVEL = message_constants.DEBUG if DEBUG else message_constants.INFO

LOGIN_REDIRECT_URL = 'index'
ACCOUNT_LOGOUT_REDIRECT_URL = 'index' # Why does allauth use django's LOGIN_REDIRECT_URL but not LOGOUT_REDIRECT_URL?

WSGI_APPLICATION = 'surveysite.wsgi.application'

HTML_MINIFY = True

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache' if DEBUG else 'django.core.cache.backends.locmem.LocMemCache',
    },
    'long': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': BASE_DIR / 'cache/',
    },
}

CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 600
CACHE_MIDDLEWARE_KEY_PREFIX = ''

# Logging
# https://docs.djangoproject.com/en/3.1/topics/logging/

# LOGGING gets merged with django's own DEFAULT_LOGGING variable
# https://github.com/django/django/blob/master/django/utils/log.py

log_directory = 'log/'
log_filename = datetime.datetime.now().strftime('%Y%m%d') + '.log'
try:
    os.mkdir(BASE_DIR / log_directory)
except FileExistsError:
    pass


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'file': {
            'format': '{levelname} {asctime}\n{message}\n',
            'style': '{',
        },
        'console': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'filters': ['require_debug_true'],
            'formatter': 'console',
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / (log_directory + log_filename),
            'formatter': 'file',
        },
    },
    'root': {
        'handlers': ['file'],
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
        },
    },
}


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_ROOT = BASE_DIR / 'static/'
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'frontend/dist/'
]


# Media files

MEDIA_ROOT = BASE_DIR / 'files/'
MEDIA_URL = '/files/'
