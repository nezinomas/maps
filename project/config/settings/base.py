import os

import environ

# ================   PATH CONFIGURATION
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ..\project_project\project\confi
SITE_ROOT = os.path.dirname(BASE_DIR)  # ..\project_project\project
PROJECT_ROOT = os.path.dirname(SITE_ROOT)  # ..\project_project

# Take ENVironment variables from .ENV file
ENV = environ.Env()
environ.Env.read_env(os.path.join(PROJECT_ROOT, '.env'))


# ================   MEDIA CONFIGURATION
MEDIA_ROOT = ENV('MEDIA_ROOT', default=os.path.join(PROJECT_ROOT, 'media'))
MEDIA_URL = "/media/"

# ================   STATIC FILE CONFIGURATION
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(SITE_ROOT, 'static')


# ================   DEBUG CONFIGURATION
DEBUG = False
TEMPLATE_DEBUG = DEBUG


# ================   SECRET CONFIGURATION
SECRET_KEY = ENV('SECRET_KEY')


# ================   project CONFIGURATION
ALLOWED_HOSTS = ['*']


# ================   DATABASE CONFIGURATION
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': os.path.join(PROJECT_ROOT, '.db'),
        },
    }
}


# ================   GENERAL CONFIGURATION
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Vilnius'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# ================   TEMPLATE CONFIGURATION
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(SITE_ROOT, 'templates')],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]


# ================   MIDDLEWARE CONFIGURATION
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ================   APP CONFIGURATION
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'project.maps'
]


# ================   URL CONFIGURATION
ROOT_URLCONF = 'project.config.urls'


# ================   WSGI CONFIGURATION
WSGI_APPLICATION = 'project.config.wsgi.application'


# ================   PASSWORD VALIDATORS CONFIGURATION
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
