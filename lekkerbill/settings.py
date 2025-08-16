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
    'storages', # For DigitalOcean Spaces
    'payfast',
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
                'invoices.context_processors.notifications_context',
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
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


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

# --- DigitalOcean Spaces Configuration (for Media Files) ---
if 'AWS_STORAGE_BUCKET_NAME' in os.environ:
    # Production settings using DigitalOcean Spaces
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME')
    AWS_S3_ENDPOINT_URL = f'https://{AWS_S3_REGION_NAME}.digitaloceanspaces.com'
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_REGION_NAME}.digitaloceanspaces.com'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
        'ACL': 'public-read', # Make files public by default
    }
    AWS_LOCATION = 'media' # Creates a 'media' folder in your space

    # This is the URL that will be used for media files
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'

    # Use the S3Boto3Storage backend for default file storage.
    STORAGES = {
        "default": {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"},
        "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
    }
else:
    # Local development settings
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# --- Logging ---
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'INFO'},
}
