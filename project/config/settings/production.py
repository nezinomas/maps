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


# ================   CRONJOBS
CRONJOBS = [
    ('0,30 * * * *', 'project.maps.cron.my_scheduled_job')
]
