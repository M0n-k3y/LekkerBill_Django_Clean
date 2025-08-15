# settings.py
import os
from pathlib import Path
from decimal import Decimal
from dotenv import load_dotenv
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file for local development
load_dotenv(BASE_DIR / '.env')

# --- Core Security Settings ---

# SECRET_KEY is loaded from an environment variable for security.
# Provide a default, insecure key for local development if not set.
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-local-dev-key')

# DEBUG is read from an environment variable. Defaults to False in production.
# The 'True'/'False' string comparison is important.
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# --- Host and CSRF Configuration ---
# This setup is flexible for any production environment (like DigitalOcean)
# and also works for local development.

# Default for local development
ALLOWED_HOSTS = ['127.0.0.1']

# Read the allowed hosts from the environment variable provided by the platform.
# DigitalOcean sets this to your app's domain via ${APP_DOMAIN}.
# The variable can be a comma-separated list, e.g., "host1.com,host2.com"
if 'ALLOWED_HOSTS' in os.environ:
    ALLOWED_HOSTS.extend(os.environ.get('ALLOWED_HOSTS').split(','))

# Automatically trust the origins for the allowed hosts for CSRF protection.
# This creates trusted origins like 'https://your-app-name.ondigitalocean.app'
CSRF_TRUSTED_ORIGINS = [f'https://{host}' for host in ALLOWED_HOSTS if host != '127.0.0.1']

# Add local development server to trusted origins if in DEBUG mode
if DEBUG:
    CSRF_TRUSTED_ORIGINS.append('http://127.0.0.1:8000')

# --- Application Definition ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # WhiteNoise must be listed before staticfiles
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'invoices',
    'payfast',
]

# --- Middleware Configuration ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise Middleware must be placed right after the security middleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# This ensures request.is_secure() works correctly behind a proxy like DigitalOcean.
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


# --- Database Configuration ---
# Switches automatically between SQLite locally and PostgreSQL in production.
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
# This is where `collectstatic` will copy all files for production.
STATIC_ROOT = BASE_DIR / "staticfiles"
# This tells Django where to find your app's static files.
STATICFILES_DIRS = []
# This enables WhiteNoise to serve compressed static files efficiently.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# For user-uploaded files (like logos).
# IMPORTANT: This works for local dev, but files will be lost on redeploys.
# A service like Amazon S3 is the standard production solution.
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
PAYFAST_PASSPHRASE = os.getenv('PAYFAST_PASSPHRASE') # Can be None
PAYFAST_TESTING = os.getenv('PAYFAST_TESTING', str(DEBUG)) == 'True'


# --- Logging ---
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'INFO'},
}
