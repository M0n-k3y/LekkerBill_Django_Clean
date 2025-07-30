import os
from pathlib import Path
from decimal import Decimal
from dotenv import load_dotenv
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    # In a real production environment, this should raise an error.
    print("WARNING: SECRET_KEY environment variable not set. Using a temporary, insecure key for build purposes.")

# SECURITY WARNING: don't run with debug turned on in production!
# We read a 'DEBUG' environment variable, defaulting to 'False' in production.
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = []

# Railway provides the public domain in the RAILWAY_PUBLIC_DOMAIN variable.
RAILWAY_PUBLIC_DOMAIN = os.getenv('RAILWAY_PUBLIC_DOMAIN')
if RAILWAY_PUBLIC_DOMAIN:
    ALLOWED_HOSTS.append(RAILWAY_PUBLIC_DOMAIN)
    # Also add the generic Railway domain for robustness.
    # The leading dot is a wildcard for subdomains.
    ALLOWED_HOSTS.append('.up.railway.app')

# Also allow localhost for local development
if DEBUG:
    ALLOWED_HOSTS.append('127.0.0.1')

# For security, Django checks the Origin header on POST requests.
CSRF_TRUSTED_ORIGINS = []
if RAILWAY_PUBLIC_DOMAIN:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RAILWAY_PUBLIC_DOMAIN}')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites', #Required for building absolute URLS for PayFast
    'invoices',
    'payfast',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Tell Django to trust the 'X-Forwarded-Proto' header from our ngrok proxy
# This ensures that request.is_secure() returns True for https requests.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


ROOT_URLCONF = 'lekkerbill.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # You can create this folder if needed
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

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

if 'DATABASE_URL' in os.environ:
    # We are in production on Railway, use the provided database URL
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True, # Recommended for production
        )
    }
else:
    # We are in local development, use SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Johannesburg'  # Adjust if needed
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# During development, this is where you place static files
STATICFILES_DIRS = [
    BASE_DIR /"invoices" / "static",  # e.g. global static assets
]

# When running collectstatic, files will be copied here
STATIC_ROOT = BASE_DIR / "staticfiles"

# Add this line to use WhiteNoise's storage backend
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (User-uploaded content like logos)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Auth settings
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# Required by django.contrib.sites to know which site's domain to use
SITE_ID = 1

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Custom App Settings ---
FREE_PLAN_ITEM_LIMIT = 5
PRO_PLAN_PRICE = Decimal('79.00')

# --- PayFast Configuration ---
PAYFAST_MERCHANT_ID = os.getenv('PAYFAST_MERCHANT_ID', '10040564')
PAYFAST_MERCHANT_KEY = os.getenv('PAYFAST_MERCHANT_KEY', '44jyetpmptdyc')
PAYFAST_PASSPHRASE = os.getenv('PAYFAST_PASSPHRASE', 'ThisIsSwiftync1')

# Use environment variable for testing flag, default to True for safety
PAYFAST_TESTING = os.getenv('PAYFAST_TESTING', 'True') == 'True'

# This setting is not actively used but is kept for clarity.
# The actual URLs are built dynamically in the views.
if RAILWAY_PUBLIC_DOMAIN:
    PAYFAST_URL_BASE = f'https://{RAILWAY_PUBLIC_DOMAIN}'
else:
    PAYFAST_URL_BASE = 'http://127.0.0.1:8000'

# --- Email Configuration (for development) ---
# This will print emails to the console instead of sending them.
# For production, you'll need to configure a real email service like SendGrid or Mailgun.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',  # This tells Django to show INFO level messages
    },
}
