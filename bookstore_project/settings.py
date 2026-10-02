import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env
load_dotenv(BASE_DIR / '.env')

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-fallback-key-booknest')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*'] if DEBUG else [host.strip() for host in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if host.strip()]

CSRF_TRUSTED_ORIGINS = [
    'https://*.ngrok-free.app',
    'https://*.ngrok-free.dev',
    'https://*.ngrok.io',
    'https://*.ngrok.app',
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]

# Application definition
INSTALLED_APPS = [
    # Unfold Admin Theme must be before django.contrib.admin
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.import_export",
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Custom Apps
    'core.apps.CoreConfig',
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

ROOT_URLCONF = 'bookstore_project.urls'

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
                'core.context_processors.booknest_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'bookstore_project.wsgi.application'

# Database Setup: Auto-detects Postgres in production or fallback to SQLite locally
DATABASE_URL = os.getenv('DATABASE_URL', f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
DATABASES = {
    'default': dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (Book covers, user uploads with Pillow optimization)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security Layers
SECURE_BROWSER_XSS_FILTER = os.getenv('SECURE_BROWSER_XSS_FILTER', 'True') == 'True'
SECURE_CONTENT_TYPE_NOSNIFF = os.getenv('SECURE_CONTENT_TYPE_NOSNIFF', 'True') == 'True'
X_FRAME_OPTIONS = os.getenv('X_FRAME_OPTIONS', 'DENY')
CSRF_COOKIE_HTTPONLY = False  # allows js access for modern async fetch with csrftoken
SESSION_COOKIE_HTTPONLY = True

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# VAPID & PWA Configuration
VAPID_PUBLIC_KEY = os.getenv('VAPID_PUBLIC_KEY', '')
VAPID_PRIVATE_KEY = os.getenv('VAPID_PRIVATE_KEY', '')
VAPID_ADMIN_EMAIL = os.getenv('VAPID_ADMIN_EMAIL', 'mailto:admin@aditibohara.com.np')

# Unfold Theme Settings for Enterprise Fortune 500 Admin
UNFOLD = {
    "SITE_TITLE": "Book Nest Enterprise CMS",
    "SITE_HEADER": "Book Nest CMS",
    "SITE_URL": "/",
    "SITE_ICON": {
        "light": lambda request: "/static/images/logo.svg",
        "dark": lambda request: "/static/images/logo.svg",
    },
    "COLORS": {
        "primary": {
            "50": "254 243 235",
            "100": "252 227 212",
            "200": "248 195 166",
            "300": "243 158 114",
            "400": "237 114 62",
            "500": "194 65 12", # Terracotta accent
            "600": "167 49 11",
            "700": "138 38 13",
            "800": "111 32 15",
            "900": "90 28 15",
            "950": "49 12 6",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Catalog & Inventory",
                "separator": True,
                "items": [
                    {
                        "title": "Books",
                        "icon": "auto_stories",
                        "link": lambda request: "/admin/core/book/",
                    },
                    {
                        "title": "Categories",
                        "icon": "category",
                        "link": lambda request: "/admin/core/category/",
                    },
                    {
                        "title": "Authors",
                        "icon": "person_edit",
                        "link": lambda request: "/admin/core/author/",
                    },
                ],
            },
            {
                "title": "Customer Interactions",
                "separator": True,
                "items": [
                    {
                        "title": "Reviews & Ratings",
                        "icon": "star_rate",
                        "link": lambda request: "/admin/core/review/",
                    },
                    {
                        "title": "Orders",
                        "icon": "shopping_cart",
                        "link": lambda request: "/admin/core/order/",
                    },
                    {
                        "title": "Contact Messages",
                        "icon": "mail",
                        "link": lambda request: "/admin/core/contactmessage/",
                    },
                    {
                        "title": "Push Subscriptions (PWA)",
                        "icon": "notifications_active",
                        "link": lambda request: "/admin/core/pushsubscription/",
                    },
                ],
            },
        ],
    },
}
