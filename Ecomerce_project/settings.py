"""
Django settings for Ecomerce_project project.

Generated by 'django-admin startproject' using Django 4.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
from datetime import timedelta
import os


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-zdpymmxyf+3f*#@2amhtlh7&n-&=n6pyc^!&&qy9nbygrde0sk'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['50.18.24.167', '127.0.0.1','localhost']

AUTH_USER_MODEL =   "customer.UserProfile"

# Email Configrations
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'pakshay@stratapps.com' # Add Authorized Email
EMAIL_HOST_PASSWORD = 'AKShay@stratapps' #Add Authorized Password

# Application definition

INSTALLED_APPS = [
    'Admins',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'customer',
    'super_admin',
    'cart',
    'payments',
    'order',
    'vendor',
    'shipment',

    # Installed Library
    'rest_framework',
    'rest_framework.authtoken',
    'knox',
    'corsheaders',
    'django_user_agents',

    # Social logins
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        #'rest_framework.authentication.TokenAuthentication',
        #'rest_framework.authentication.SessionAuthentication',
        'knox.auth.TokenAuthentication',
    ),
}

# If you want to allow access for all domains, set the following variable to TRUE
CORS_ORIGIN_ALLOW_ALL = True

CORS_ORIGIN_WISHLIST = [
    'http://localhost:4200',
    'http://127.0.0.1:5000',
    'http://127.0.0.1:8000',
    'http://50.18.24.167:80'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    #CORS MiddleWare
    'corsheaders.middleware.CorsMiddleware',

    #  Messages in Django
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    # User Agent Middle Ware
    'django_user_agents.middleware.UserAgentMiddleware',
]

ROOT_URLCONF = 'Ecomerce_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,"templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'django.template.context_processors.request',
            ],
        },
    },
]
WSGI_APPLICATION = 'Ecomerce_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
   'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'akshay_v1', 
        'USER': 'postgres', 
        'PASSWORD': 'Welcome!234',
        'HOST': 'e-commerce.cj3oddyv0bsk.us-west-1.rds.amazonaws.com', 
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.ScryptPasswordHasher',
]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

MEDIA_ROOT =  os.path.join(BASE_DIR, 'media')
MEDIA_URL = 'media/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SECURE_CROSS_ORIGIN_OPENER_POLICY=None

# Value determines whether the server allows cookies in the cross-site HTTP requests
CORS_ALLOW_CREDENTIALS = True

# Methods allowed for CORS
CORS_ALLOW_METHODS = [
    'DELETE',
    'OPTIONS',
    'PATCH',
    'GET',
    'POST',
    'PUT',  
]

# Non-standard headers allowed in the request
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Customizing Knox-Token Fields

# from rest_framework.settings import api_settings
REST_KNOX = {
  'SECURE_HASH_ALGORITHM': 'cryptography.hazmat.primitives.hashes.SHA512',
  'AUTH_TOKEN_CHARACTER_LENGTH': 8,
  'TOKEN_TTL': timedelta(minutes=120),
  'USER_SERIALIZER': 'knox.serializers.UserSerializer',
  'TOKEN_LIMIT_PER_USER': None,
  'AUTO_REFRESH': False,
#   'EXPIRY_DATETIME_FORMAT': api_settings.DATETME_FORMAT,
}



AUTHENTICATION_BACKENDS = [
   
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
   
]

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

SITE_ID = 3

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'


SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}



# STRIPE_PUBLISHIBLE_KEY = 'pk_test_51N2qeWSDVQXVPSKWD6CaXuICuzl5GmPR3vG93jiJRKNwJCZcZa6e2wsF2WioBDjFplYdHKWzdI7pVshlYzSQG8cJ00R0X4pqLo'
# STRIPE_SECRET_KEY = 'sk_test_51N2qeWSDVQXVPSKWZLRZYhEEi6earcJWrqUtEUHdoBGOcrw9L6gSx9Fdm7lWxPnWets56BBm6VPCiyqTCLVZWYt200MmV72AIg'


##### INDIAN KEYS
STRIPE_PUBLISHIBLE_KEY = 'pk_test_51N14xtSBTvvAxHEHsTCkXf5wERARYeTZxs26hMoysIKiZ45H1EaFXngXiF8wHKgqQUbEuacx1qM7aXkDD0BUmW0d00R2wVp0zX'
STRIPE_SECRET_KEY = 'sk_test_51N14xtSBTvvAxHEHEKNzwz0FVf9cWlZr1G54lsR1jMYrMZOO2wmXWwYJBPUQbSFXWz1Ra0o36ASV8g6nWFgpcjqm000Unwl8Pi'


######  US keys
STRIPE_PUBLISHIBLE_US_KEY = 'pk_test_51MyDdKDbTkeiiJOUPYTNMVNzxGCk1Ga3ke9jOuCwDxzvOvh4dl02gG3m3xDRfvAQVDHjCdCiQEGd6PQ98Zzap6xz00uEULL0zL'
STRIPE_SECRET_US_KEY = 'sk_test_51MyDdKDbTkeiiJOUlkEXErPox3NmgNMjgZsvEmO4mNWKGWQ0kyAuVLmkimPuwr6as4xsorGHgj3Eh6XfazyHX7Kb00sulvTDHh'


# The validity of this token is 10 days (created-at : 08-09-2023)
SHIPMENT_TOKEN = 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL2FwaXYyLnNoaXByb2NrZXQuaW4vdjEvZXh0ZXJuYWwvYXV0aC9sb2dpbiIsImlhdCI6MTY5NDE0MjU3MCwiZXhwIjoxNjk1MDA2NTcwLCJuYmYiOjE2OTQxNDI1NzAsImp0aSI6IjZwblBYb1FvVG9LZEU5YVYiLCJzdWIiOjMzODMzNjgsInBydiI6IjA1YmI2NjBmNjdjYWM3NDVmN2IzZGExZWVmMTk3MTk1YTIxMWU2ZDkifQ.3-yzQ-WC-4Wk1wgjTS06bE_HExr6BX54OXYImy83vNU'


prperpage = 10


INDIAN_tax_id = "txr_1NODQuSBTvvAxHEHPFqxQS5x"
US_tax_id = "txr_1NODQuDbTkeiiJOUzjruPrFC"