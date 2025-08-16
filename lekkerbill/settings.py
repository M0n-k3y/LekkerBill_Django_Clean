# settings.py
import os
from pathlib import Path
from decimal import Decimal
from dotenv import load_dotenv
import dj_database_url

# --- Base Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file for local development
load_dotenv(BASE_DIR / '.env')

# --- Core Security Settings ---
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-local-dev-key')
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# --- Host and CSRF Configuration ---
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# DigitalOcean usually injects APP_DOMAIN automatically
app_domain = os.getenv("APP_DOMAIN")
if app_domain:
    ALLOWED_HOSTS.append(app_domain)

# Explicit override (comma-separated)
env_hosts = os.getenv("ALLOWED_HOSTS")
if env_hosts:
    ALLOWED_HOSTS.extend(env_hosts.split(","))

# Remove duplicates / whitespace
ALLOWED_HOSTS = list({h.strip() for h in ALLOWED_HOSTS if h.strip()})

# CSRF Trusted Origins (required for HTTPS on DO)
CSRF_TRUSTED_ORIGINS = [
    f"https://{host}" for host in ALLOWED_HOSTS if host not in ["127.0.0.1", "localhost"]
]

if DEBUG:
    CSRF_TRUSTED_ORIGINS.append("http://127.0.0.1:8000")

# --- Application Definition ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',   # Must be before staticfiles
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'invoices',
    # 'payfast',  # Uncomment when ready
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Must be right after SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# This ensures request.is_secure() works correctly behind a proxy like DO
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ROOT_URLCONF = 'lekkerbill.urls'

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
        },
    },
]

WSGI_APPLICATION = 'lekkerbill.wsgi.application'

# --- Database ---
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600, conn_health_checks=True)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# --- Password Validation ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- Internationalization & Static/Media Files ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Johannesburg'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = []
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- Auth & Site Settings ---
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
SITE_ID = 1
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Custom App & PayFast Settings ---
FREE_PLAN_ITEM_LIMIT = 5
PRO_PLAN_PRICE = Decimal('79.00')

PAYFAST_MERCHANT_ID = os.getenv('PAYFAST_MERCHANT_ID', '10000100')
PAYFAST_MERCHANT_KEY = os.getenv('PAYFAST_MERCHANT_KEY', '46f0cd694581a')
PAYFAST_PASSPHRASE = os.getenv('PAYFAST_PASSPHRASE')  # Can be None
PAYFAST_TESTING = os.getenv('PAYFAST_TESTING', str(DEBUG)) == 'True'

# --- Logging ---
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'INFO'},
}
