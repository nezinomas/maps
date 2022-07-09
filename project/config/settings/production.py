from .base import *


# ================   DEBUG CONFIGURATION
DEBUG = False
TEMPLATE_DEBUG = DEBUG


# ================   project CONFIGURATION
ALLOWED_HOSTS = ['*']


# ================   APP CONFIGURATION
INSTALLED_APPS += [
    'django_crontab',
]


TEMPLATES[0]['OPTIONS']['loaders'] = [
    ['django.template.loaders.cached.Loader', [
        'django_spaceless_templates.loaders.filesystem.Loader',
        'django_spaceless_templates.loaders.app_directories.Loader', ],
     ],
]


SECURE_HSTS_SECONDS = 60
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_PRELOAD = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'


# EMAIL settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = 'Invite <invite@bookkeeping.com>'


# ================   CRONJOBS
CRONJOBS = [
    ('0,30 * * * *', 'project.maps.cron.my_scheduled_job', '> /dev/null 2>&1'),
    ('5,30 * * * *', 'project.maps.cron.push_comment_qty', '> /dev/null 2>&1'),
]
