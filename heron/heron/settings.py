import os

from heron import local_settings

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "t4h)8sau*-6#-tb&$x32itmfm+d!!8v@0edm0!4eteu2$q__!l"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
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
        "django": {"handlers": ["console"], "level": local_settings.LOG_LEVEL},
    },
}


STATIC_URL = "/static/"

USER_TOKEN = "<<user>>"
LINK_TOKEN = "<<link>>"
TAG_TOKEN = "<<tag>>"

# One of: ["markov_chain"]
TEXT_GENERATION_FUNCTION = local_settings.text_generation_function

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


