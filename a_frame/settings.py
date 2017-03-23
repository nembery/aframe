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
    "screens",
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

# setup log file at /var/log/aframe.log
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/aframe.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARN',
            'propagate': True,
        },
        '': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    },
}

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
        "name": "SSHRemoteExecution",
        "label": "SSH Remote Execution",
        "options": [
            {
                "label": "Request Type",
                "name": "request_type",
                "type": "select",
                "choices": [
                    {
                        "name": "cli",
                        "label": "Execute CLI remotely via SSH",
                        "arguments": []
                    },
                    {
                        "name": "scp",
                        "label": "SCP template to remote path",
                        "arguments": []
                    },
                    {
                        "name": "scp_and_execute",
                        "label": "SCP and Execute template on remote host",
                        "arguments": []
                    }
                ]
            },
            {
                "label": "Remote File Path",
                "name": "file_path",
                "type": "text",
                "default": "/var/tmp/aframe/{{ script_name }}"
            }
        ]
    },
    {
        "name": "GitAction",
        "label": "Git Repository Manipulation",
        "options": [
            {
                "label": "Remote URL",
                "name": "remote_url",
                "type": "text",
                "default": "https://user:pass@github.com/nembery/aframe.git"
            },
            {
                "label": "Target Branch",
                "name": "target_branch",
                "type": "text",
                "default": "master"
            },
            {
                "label": "Target Directory",
                "name": "target_directory",
                "type": "text",
                "default": "/"
            },
            {
                "label": "Target Filename",
                "name": "target_filename",
                "type": "text",
                "default": "README.md"
            },
            {
                "label": "Commit Message",
                "name": "commit_message",
                "type": "text",
                "default": "Committed from AFrame"
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
                    },
                    {
                        "name": "oauth2",
                        "label": "OAuth2",
                    },
                    {
                        "name": "ruckus",
                        "label": "Ruckus REST Cookie",
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
                "label": "Keystone Host",
                "name": "keystone_host",
                "type": "text",
                "default": "n/a"
            },
             {
                "label": "Keystone Project Scope",
                "name": "keystone_project",
                "type": "text",
                "default": "admin"
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

REGISTERED_APP_THEMES = (
    {
        "label": "Default Theme",
        "base_template": "base.html",
    },
    {
        "label": "Dark",
        "base_template": "themes/dark.html",
    },
    {
        "label": "Grey/Blue",
        "base_template": "themes/grey_blue.html",
    },
    {
        "label": "Grey/Red",
        "base_template": "themes/grey_red.html",
    },
    {
        "label": "Grey/Green",
        "base_template": "themes/grey_green.html",
    },
    {
        "label": "Grey/Orange",
        "base_template": "themes/grey_orange.html",
    },
    {
        "label": "White/Blue",
        "base_template": "themes/white_blue.html",
    },
    {
        "label": "White/Red",
        "base_template": "themes/white_red.html",
    },
{
        "label": "White/Green",
        "base_template": "themes/white_green.html",
    },
    {
        "label": "White/Orange",
        "base_template": "themes/white_orange.html",
    }
)

WIDGETS = (
    {
        "label": "Simple Text Input",
        "configurable": False,
        "id": "text_input",
        "configuration_template": None,
        "render_template": "text_input.html"
    },
    {
        "label": "Text Input with Regex Validation",
        "configurable": True,
        "id": "text_input_regex",
        "configuration_template": "text_input_regex_config.html",
        "render_template": "text_input_regex.html"
    },
    {
        "label": "Text Input with Numeric Validation",
        "configurable": True,
        "id": "text_input_numeric",
        "configuration_template": "text_input_numeric_config.html",
        "render_template": "text_input_numeric.html"
    },
    {
        "label": "IPv4 Address",
        "configurable": False,
        "id": "ipv4_input",
        "configuration_template": None,
        "render_template": "ipv4_input.html"
    },
    {
        "label": "Password Input",
        "configurable": False,
        "id": "password_input",
        "configuration_template": None,
        "render_template": "password_input.html"
    },
    {
        "label": "Complex Password Input",
        "configurable": True,
        "id": "complex_password_input",
        "configuration_template": "complex_password_input_config.html",
        "render_template": "complex_password_input.html"
    },
    {
        "label": "Text Area Input",
        "configurable": False,
        "id": "text_area_input",
        "configuration_template": None,
        "render_template": "text_area_input.html"
    },
    {
        "label": "Configurable Select List",
        "configurable": True,
        "id": "select_input",
        "configuration_template": "select_input_config.html",
        "render_template": "select_input.html"
    },
    {
        "label": "Preloaded Value from Automation",
        "configurable": True,
        "id": "preload_value",
        "configuration_template": "preload_value_config.html",
        "render_template": "preload_value.html"
    },
    {
        "label": "Preloaded List from Automation",
        "configurable": True,
        "id": "preload_list",
        "configuration_template": "preload_list_config.html",
        "render_template": "preload_list.html"
    },
    {
        "label": "Endpoint Name Search",
        "configurable": False,
        "id": "endpoint_name_search_input",
        "render_template": "endpoint_name_search_input.html"
    },
    {
        "label": "Endpoint ID Search",
        "configurable": False,
        "id": "endpoint_id_search_input",
        "render_template": "endpoint_id_search_input.html"
    },
    {
        "label": "Endpoint IP Search",
        "configurable": False,
        "id": "endpoint_ip_search_input",
        "render_template": "endpoint_ip_search_input.html"
    },
)

SCREEN_WIDGETS = (
    {
        "label": "Menu",
        "configurable": True,
        "id": "menu",
        "configuration_template": "menu_config.html",
        "render_template": "menu.html"
    },
    {
        "label": "Static Image",
        "configurable": True,
        "id": "static_image",
        "configuration_template": "static_image_config.html",
        "render_template": "static_image.html"
    }
)
