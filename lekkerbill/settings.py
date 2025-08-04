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
    print("WARNING: SECRET_KEY environment variable not set. Using a temporary, insecure key for build purposes.")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = []
RAILWAY_PUBLIC_DOMAIN = os.getenv('RAILWAY_PUBLIC_DOMAIN')
if RAILWAY_PUBLIC_DOMAIN:
    ALLOWED_HOSTS.append(RAILWAY_PUBLIC_DOMAIN)
    ALLOWED_HOSTS.append('.up.railway.app')

if DEBUG:
    ALLOWED_HOSTS.append('127.0.0.1')

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
    'django.contrib.sites',
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

# Database
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

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Johannesburg'
USE_I18N = True
USE_TZ = True

# --- Static files (CSS, JavaScript, Images) ---
STATIC_URL = '/static/'

# ✅ NEW, UNAMBIGUOUS CONFIGURATION:
# We now tell Django to look in the single, top-level 'static' directory.
# This is the most reliable way to manage project-wide static files.
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# This is the directory where `collectstatic` will copy all static files for production.
STATIC_ROOT = BASE_DIR / "staticfiles"

# Use WhiteNoise's storage backend for efficient caching and gzipping.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- Media files (User-uploaded content like logos) ---
# ❗️ IMPORTANT: This configuration is for LOCAL DEVELOPMENT ONLY.
# In production on Railway, the filesystem is "ephemeral," meaning any uploaded
# files will be DELETED every time you deploy or restart the app.
# The professional solution is to use a cloud storage service like Amazon S3.
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- Auth settings ---
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

SITE_ID = 1
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Custom App Settings ---
FREE_PLAN_ITEM_LIMIT = 5
PRO_PLAN_PRICE = Decimal('79.00')

# --- PayFast Configuration ---
PAYFAST_MERCHANT_ID = os.getenv('PAYFAST_MERCHANT_ID')
PAYFAST_MERCHANT_KEY = os.getenv('PAYFAST_MERCHANT_KEY')
PAYFAST_PASSPHRASE = os.getenv('PAYFAST_PASSPHRASE')
PAYFAST_TESTING = os.getenv('PAYFAST_TESTING', str(DEBUG)) == 'True'

if not DEBUG and not all([PAYFAST_MERCHANT_ID, PAYFAST_MERCHANT_KEY]):
    raise ValueError("In production, PAYFAST_MERCHANT_ID and PAYFAST_MERCHANT_KEY must be set.")

# --- Email & Logging ---
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'INFO'},
}