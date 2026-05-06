"""
Django settings for service_system project.
Система управления сервисными заявками ООО «ТатАИСнефть»
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-42eso+$8v1b^^jlc7i8-ay+(e9p4bq$%90mt&#zy5x17+j0s7u'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Наши приложения
    'accounts',
    'tickets',
    'notifications',
    'reports',
    'knowledgebase',
    'maps',
    # Сторонние
    'crispy_forms',
    'crispy_bootstrap5',
    'chartjs',
    'rest_framework',
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

ROOT_URLCONF = 'service_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'notifications.context_processors.unread_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'service_system.wsgi.application'


# Database — Microsoft SQL Server
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'ServiceSystemDB_5',
        'HOST': r'WIN-BBAL9U7JEPL\SQLEXPRESS',
        'USER': '',
        'PASSWORD': '',
        'PORT': '',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'trusted_connection': 'yes',
        },
    }
}

AUTH_USER_MODEL = 'accounts.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Auth redirects
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Email — SMTP via Yandex (change to your provider)
# For development: use EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# For production: use EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = 'morevnikitka@yandex.ru'      # <-- CHANGE to your email
EMAIL_HOST_PASSWORD = 'istzdpqftrpihnio'        # <-- CHANGE to your app password
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER

# SMS Settings (placeholder — configure your SMS provider)
# Supported: smsaero, turbosms, infosmska
SMS_PROVIDER = 'smsaero'  # 'console' = log to DB only, 'smsaero' = SMSAero.ru, etc.
SMSAERO_EMAIL = 'book1829199292828299@gmail.com'         # <-- Your SMSAero login/email
SMSAERO_API_KEY = 'mu3oiYhf_TvR5vhVnDk_ef1Z2CrNBDWM'       # <-- Your SMSAero API key
SMSAERO_SENDER = 'TatAIS'  # <-- Registered sender name

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
