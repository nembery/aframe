"""
Django settings for A-Frame project.

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
SECRET_KEY = "6byb6f6)0z@0e!z1^%+j)18z%+#wusz5jdr@nl+y*_cvp#o*o@"

# SECURITY WARNING: don"t run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "common",
    "tools",
    "endpoints",
    "input_forms",
)

MIDDLEWARE_CLASSES = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)

ROOT_URLCONF = "a_frame.urls"

WSGI_APPLICATION = "a_frame.wsgi.application"


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = "/static/"

CACHE_BACKEND = "file:///var/tmp/a_frame_django_cache"

# add your class name here so it will be loaded at runtime
REGISTERED_ENDPOINT_PROVIDERS = (
    {
        "class": "FileDiscovery",
        "name": "CSV file connector",
    },
    {
        "class": "StaticList",
        "name": "Statically defined List",
    },
    {
        "class": "NmapDiscovery",
        "name": "nmap network discovery connector",
    },
    {
        "class": "JunosSpaceDeviceList",
        "name": "Junos Space Device List",
    }
)
ACTION_PROVIDERS = (
    {
        "name": "NetconfAction",
        "label": "NetConf",
        "options": [
            {
                "label": "Request Type",
                "name": "request_type",
                "type": "select",
                "choices": [
                    {
                        "name": "apply_template",
                        "label": "Apply Configuration",
                        "arguments": []
                    },
                    {
                        "name": "execute_op_command",
                        "label": "Run Operational Command",
                        "arguments": []
                    },
                    {
                        "name": "execute_cheat_command",
                        "label": "Run a cheat command (cli)",
                        "arguments": []
                    },
                    {
                        "name": "assert_set_configuration",
                        "label": "Assert a RegEx expression matches the Configuration in set format",
                        "arguments": []
                    },
                    {
                        "name": "assert_xpath_configuration",
                        "label": "Assert a xPath expression matches the Configuration in XML format",
                        "arguments": []
                    }
                ]
            }
        ]
    },
    {
        "name": "ShellExecution",
        "label": "Executes Template in a Shell on the local server",
        "options": []
    },
    {
        "name": "RestAction",
        "label": "REST API Action",
        "options": [
            {
                "label": "Authentication Type",
                "name": "auth_type",
                "type": "select",
                "choices": [
                    {
                        "name": "none",
                        "label": "None",
                    },
                    {
                        "name": "basic",
                        "label": "Basic",
                    },
                    {
                        "name": "keystone",
                        "label": "Keystone",
                    }
                ]
            },
            {
                "label": "Username",
                "name": "username",
                "type": "text",
                "default": "guest"
            },
            {
                "label": "Password",
                "name": "password",
                "type": "text",
                "default": "password"
            },
            {
                "label": "Request type",
                "name": "request_type",
                "type": "select",
                "choices": [
                    {
                        "name": "GET",
                        "label": "Perform GET request",
                    },
                    {
                        "name": "POST",
                        "label": "Perform POST request",
                    },
                    {
                        "name": "DELETE",
                        "label": "Perform DELETE request",
                    }
                ]
            },
            {
                "label": "Protocol",
                "name": "protocol",
                "type": "select",
                "choices": [
                    {
                        "name": "https",
                        "label": "HTTPS",
                    },
                    {
                        "name": "http",
                        "label": "HTTP",
                    }
                ]
            },
            {
                "label": "Endpoint Host",
                "name": "host",
                "type": "text",
                "default": "127.0.0.1"
            },
            {
                "label": "URL Path",
                "name": "url",
                "type": "text",
                "default": "/rest/api/path"
            },
            {
                "label": "Content Type",
                "name": "content_type",
                "type": "text",
                "default": "application/json",
            },
                        {
                "label": "Accepts Content Type",
                "name": "accepts_type",
                "type": "text",
                "default": "application/json",
            }
        ]
    }
)

DEVICE_LIST_PAGING_SIZE = 10

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # insert your TEMPLATE_DIRS here
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
