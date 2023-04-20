from pathlib import Path

from decouple import config as env

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = (
    "django-insecure-bfjks3u61xj62=&ef!5dkwcum$7f(lpf+56r$td0andc%2%o+p"
)
DEBUG = True

AUTH_USER_MODEL = "user.UserModel"

ALLOWED_HOSTS = ["*"]

DJANGO_APPS = [
    "core_api.config.suit.SuitConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
THIRD_APPS = [
    "rest_framework",
    "rest_framework.authtoken",
    "drf_yasg",
    "colorfield",
]
LOCAL_APPS = [
    "apps.user",
    "apps.service",
    "apps.material",
    "apps.visual_structure",
    "apps.buying",
    "apps.social",
]


INSTALLED_APPS = DJANGO_APPS + THIRD_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core_api.urls"

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

WSGI_APPLICATION = "core_api.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
        ),
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

TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "apikey"
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
SERVER_EMAIL = "tecnologia-alertas@startnow.do"

DEFAULT_LOGIN_CREDENTIAL_CONFIGS = [
    {
        "credential_config_type": "login",
        "field": "email",
        "label": "Write your email",
        "field_html_type": "email",
    },
    {
        "credential_config_type": "login",
        "field": "password",
        "label": "Write your password",
        "field_html_type": "password",
    },
]

DEFAULT_REGISTER_CREDENTIAL_CONFIGS = [
    {
        "credential_config_type": "register",
        "field": "email",
        "label": "Write your email",
        "field_html_type": "email",
        "rule": r"^[a-zA-Z0-9._-]+@[a-zA-Z0-9]+\.[a-zA-Z\.a-zA-Z]{1,3}$",
        "no_match_message": "Invalid email",
    },
    {
        "credential_config_type": "register",
        "field": "password",
        "label": "Write your password",
        "field_html_type": "password",
        "rule": r"(?=^.{8,}$)((?=.*\d)(?=.*\W+))(?![.\n])(?=.*[A-Z])(?=.*[a-z]).*$",
        "no_match_message": "Invalid password",
    },
    {
        "credential_config_type": "register",
        "field": "confirm_password",
        "label": "Confirm your password",
        "field_html_type": "password",
        "no_match_message": "Confirm password",
    },
]
DEFAULT_CREDENTIAL_CONFIGS = (
    DEFAULT_LOGIN_CREDENTIAL_CONFIGS + DEFAULT_REGISTER_CREDENTIAL_CONFIGS
)
