"""
Django settings for tourism_analyzer.

Deployment-specific values come from environment variables (optionally a
local .env file). See .env.example.
"""
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


def env_list(name, default=''):
    return [item.strip() for item in os.environ.get(name, default).split(',') if item.strip()]


DEBUG = env_bool('DJANGO_DEBUG', False)

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        # Local development only. Never used when DJANGO_DEBUG is off.
        SECRET_KEY = 'django-insecure-local-dev-only-key'
    else:
        raise ImproperlyConfigured(
            'DJANGO_SECRET_KEY is not set. Set it in the environment (or .env), '
            'or set DJANGO_DEBUG=true for local development.'
        )

ALLOWED_HOSTS = env_list('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1')
CSRF_TRUSTED_ORIGINS = env_list('DJANGO_CSRF_TRUSTED_ORIGINS')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'tourism_dashboard',
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

ROOT_URLCONF = 'tourism_analyzer.urls'

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

WSGI_APPLICATION = 'tourism_analyzer.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.environ.get('SQLITE_PATH', BASE_DIR / 'db.sqlite3'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Uploaded CSVs are parsed in memory; reject anything larger than this.
MAX_UPLOAD_BYTES = int(os.environ.get('MAX_UPLOAD_BYTES', 5 * 1024 * 1024))
DATA_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_BYTES

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

LOGIN_REDIRECT_URL = 'dashboard'
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'login'

if not DEBUG:
    SESSION_COOKIE_SECURE = env_bool('DJANGO_SECURE_COOKIES', True)
    CSRF_COOKIE_SECURE = env_bool('DJANGO_SECURE_COOKIES', True)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # Cookies are never read by JavaScript here, and SameSite=Lax stops them
    # riding along on cross-site requests — the other half of CSRF defence.
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SAMESITE = 'Lax'

    # `manage.py check --deploy` flagged both of these as missing (W008, W004).
    #
    # They default on but stay overridable, because enabling HSTS is effectively
    # irreversible for the length of max-age: a browser that has seen the header
    # refuses plain HTTP to this host until it expires. Anyone deploying onto a
    # plain-HTTP host needs to turn it off up front rather than discover the
    # lockout afterwards.
    SECURE_SSL_REDIRECT = env_bool('DJANGO_SSL_REDIRECT', True)
    SECURE_HSTS_SECONDS = int(os.environ.get('DJANGO_HSTS_SECONDS', 31536000))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool('DJANGO_HSTS_INCLUDE_SUBDOMAINS', True)
    # Preload is deliberately NOT on by default: submitting a domain to the
    # browser preload list is genuinely permanent, so it should be a choice.
    SECURE_HSTS_PRELOAD = env_bool('DJANGO_HSTS_PRELOAD', False)

    # Defence in depth alongside Django's own template escaping.
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
    X_FRAME_OPTIONS = 'DENY'
