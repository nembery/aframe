"""
Django settings for a_frame project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '6byb6f6)0z@0e!z1^%+j)18z%+#wusz5jdr@nl+y*_cvp#o*o@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'common',
    'tools',
    'endpoints',
    'input_forms',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'a_frame.urls'

WSGI_APPLICATION = 'a_frame.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

CACHE_BACKEND = 'file:///var/tmp/a_frame_django_cache'

# add your class name here so it will be loaded at runtime
DEVICE_DISCOVERY_PROVIDERS = (
    {
        'name': 'FileDiscovery',
        'label': 'File: someFilename',
        'data': 'endpointList.txt',
    },
    {
        'name': 'StaticDiscovery',
        'label': 'Some statically configured list of endpoints',
        'data': [
            ['1', 'pit-spr-05-001', '10.1.5.1', 'admin', 'Clouds123', 'acx1000'],
            ['2', 'pit-spr-05-006', '10.1.5.6', 'admin', 'Clouds123', 'acx1000'],
            ['3', 'pit-spr-05-131', '10.1.5.131', 'admin', 'Clouds123', 'acx2200'],
            ['4', 'pit-spr-05-142', '10.1.5.142', 'admin', 'Clouds123', 'acx2200'],
        ]
    },
    {
        'name': 'NmapDiscovery',
        'label': 'All endpoints in the 10.0.1.0/24 range',
        'data': {
            'network': '10.0.1.0/24',
            'username': 'root',
            'password': 'Clouds123',
            'endpoint_type': 'NA',
            'cache_timeout': 180
        }
    },

)
ACTION_PROVIDERS = (
    {
        'name': 'NetconfAction',
        'label': 'NetConf',
        'options': [
            {
                'label': 'Request Type',
                'name': 'request_type',
                'type': 'select',
                'choices': [
                    {
                        'name': 'apply_template',
                        'label': "Apply Configuration",
                        'arguments': []
                    },
                    {
                        'name': 'execute_op_command',
                        'label': "Run Operational Command",
                        'arguments': []
                    },
                    {
                        'name': 'execute_cheat_command',
                        'label': "Run a cheat command (cli)",
                        'arguments': []
                    }
                ]
            }
        ]
    },
    {
        'name': 'JunosSpaceRestClient',
        'label': 'Rest Client for Junos Space',
        'global': {
            'username': 'super',
            'password': 'juniper123!!',
            'ip': '172.25.91.186',
            'protocol': 'https',
        },
        'options': [
            {
                'label': 'Choose Request type',
                'name': 'request_type',
                'type': 'select',
                'choices': [
                    {
                        'name': 'GET',
                        'label': 'Perform GET request',
                    },
                    {
                        'name': 'POST',
                        'label': 'Perform POST request',
                    },
                    {
                        'name': 'DELETE',
                        'label': 'Perform DELETE request',
                    }
                ]
            },
            {
                'label': 'URL Path',
                'name': 'url',
                'type': 'text',
                'default': '/rest/api/path'
            },
            {
                'label': 'Content Type',
                'name': 'content_type',
                'type': 'select',
                'choices': [
                    {
                        'name': 'application/json',
                        'label': 'application/json',
                    },
                    {
                        'name': 'application/x-www-form-urlencoded',
                        'label': 'application/x-www-form-urlencoded',
                    },
                    {
                        'name': 'application/xml',
                        'label': 'application/xml',
                    }
                ]
            },

        ]
    },
    {
        'name': 'genericRestClient',
        'label': 'Generic client for REST API Endpoints',
        'options': [
            {
                'label': 'Authentication Type',
                'name': 'auth_type',
                'type': 'select',
                'choices': [
                    {
                        'name': 'none',
                        'label': 'None',
                    },
                    {
                        'name': 'basic',
                        'label': 'Basic',
                    },
                    {
                        'name': 'keystone',
                        'label': 'Keystone',
                    }
                ]
            },
            {
                'label': 'Username',
                'name': 'username',
                'type': 'text',
                'default': 'guest'
            },
            {
                'label': 'Password',
                'name': 'password',
                'type': 'text',
                'default': 'password'
            },
            {
                'label': 'Choose Request type',
                'name': 'request_type',
                'type': 'select',
                'choices': [
                    {
                        'name': 'perform_get',
                        'label': 'Perform GET request',
                    },
                    {
                        'name': 'perform_post',
                        'label': 'Perform POST request',
                    },
                    {
                        'name': 'perform_delete',
                        'label': 'Perform DELETE request',
                    }
                ]
            },
            {
                'label': 'URL Path',
                'name': 'url',
                'type': 'text',
                'default': '/rest/api/path'
            },
            {
                'label': 'Content Type',
                'name': 'content_type',
                'type': 'select',
                'choices': [
                    {
                        'name': 'application/json',
                        'label': 'application/json',
                    },
                    {
                        'name': 'application/x-www-form-urlencoded',
                        'label': 'application/x-www-form-urlencoded',
                    },
                    {
                        'name': 'application/xml',
                        'label': 'application/xml',
                    }
                ]
            },

        ]
    }
)

DEVICE_LIST_PAGING_SIZE = 10
