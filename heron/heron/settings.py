import os
import sys
import dj_database_url

from django.core.management.utils import get_random_secret_key


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

# Used to determine when to connect to Postgres vs. SQLite
DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "False") == "True"


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "bots",
]

MIDDLEWARE_CLASSES = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.auth.middleware.SessionAuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "heron.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "heron.wsgi.application"


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
# On Digital Ocean, connect to Postgres, so stuff is stored on disk

if DEVELOPMENT_MODE is True:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }
elif len(sys.argv) > 0 and sys.argv[1] != 'collectstatic':
    if os.getenv("DATABASE_URL", None) is None:
        raise Exception("DATABASE_URL environment variable not defined")
    DATABASES = {
        "default": dj_database_url.parse(os.environ.get("DATABASE_URL")),
    }


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

LOGGING = {
    "version": 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": os.getenv("LOG_LEVEL", "DEBUG")},

    },
}


STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

USER_TOKEN = "<<user>>"
LINK_TOKEN = "<<link>>"
TAG_TOKEN = "<<tag>>"

TEXT_GENERATION_FUNCTION = "markov_chain"

'''
TWEEPY_CONSUMER_KEY = local_settings.tweepy_consumer_key
TWEEPY_CONSUMER_SECRET = local_settings.tweepy_consumer_secret
TWEEPY_ACCESS_TOKEN = local_settings.tweepy_access_token
TWEEPY_ACCESS_TOKEN_SECRET = local_settings.tweepy_access_token_secret

WATSON_TONE_USERNAME = local_settings.watson_tone_username
WATSON_TONE_PASSWORD = local_settings.watson_tone_password
WATSON_UNDERSTANDING_USERNAME = local_settings.watson_understanding_username
WATSON_UNDERSTANDING_PASSWORD = local_settings.watson_understanding_password

WATSON_EMOTIONS = ["anger", "joy", "sadness", "fear", "disgust"]

DISCORD_CONVERSATION_NAME = local_settings.discord_conversation_name
DISCORD_CONVERSATION_STATES = local_settings.discord_conversation_states
'''
