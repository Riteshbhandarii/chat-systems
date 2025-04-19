"""
Django settings for chat_project project.
Railway-ready version - Only essential deployment changes made
"""

from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

# Temporary debugging: Check if DATABASE_URL is being read
print("DATABASE_URL from environment:", os.environ.get('DATABASE_URL'))

# Load environment variables (for local development)
load_dotenv()

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# ====== Deployment Essentials ======
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-key-only')  # Set real one in Railway
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = ['*']  # For initial deployment (replace with your Railway URL later)

# ====== Original Settings Below ======
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'rest_framework',
    'rest_framework.authtoken',
    "messaging",
    "channels",
]

ASGI_APPLICATION = "chat_project.asgi.application"

# Redis config (Railway will provide REDIS_URL)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.getenv('REDIS_URL', 'redis://localhost:6379')],
        },
    },
}

# PostgreSQL (Railway auto-configures)
DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,
        #ssl_require=True, # Recommended for production
        # default='postgresql://chat_user:@localhost:5432/chat_project' # Comment this out or remove
    )
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Added for static files
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "chat_project.urls"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'messaging/templates')],
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

WSGI_APPLICATION = "chat_project.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
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
# In your settings.py
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Add the CSRF_TRUSTED_ORIGINS setting:
CSRF_TRUSTED_ORIGINS = ['https://umbrachat.up.railway.app']

# Static files (Railway requirement)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

print("MIDDLEWARE ORDER:", MIDDLEWARE)