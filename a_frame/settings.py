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

ALLOWED_HOSTS = ['*']

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
            'filename': '/tmp/aframe.log',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'WARN',
            'propagate': True,
        },
        '': {
            'handlers': ['file', 'console'],
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
    },
    {
        "class": "SaltMinion",
        "name": "Salt Minions",
    }
)
ACTION_PROVIDERS = (
    {
        "name": "NetconfAction",
        "class": "NetconfAction",
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
        "class": "SSHRemoteExecution",
        "label": "Remote/SSH Shell Script",
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
        "class": "GitAction",
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
        "class": "ShellExecution",
        "label": "Local Shell Script",
        "options": []
    },
    {
        "name": "RestAction",
        "class": "RestAction",
        "label": "Advanced REST",
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
                        "name": "bearer",
                        "label": "Bearer",
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
                    },
                    {
                        "name": "saltapi",
                        "label": "Salt-api",
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
                "type": "secret",
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
                        "name": "http",
                        "label": "HTTP",
                    },
                    {
                        "name": "https",
                        "label": "HTTPS",
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
            },
            # Work in progress for custom headers and extensible list of configuration elements
            # {
            #     "label": "Custom Header",
            #     "name": "header_list",
            #     "type": "kv_list",
            #     "default": "[]",
            # }
        ]
    },
    {
        "name": "BasicRestAction",
        "class": "RestAction",
        "label": "Basic REST",
        "options": [
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
                "label": "Full URL",
                "name": "full_url",
                "type": "text",
                "default": "https://127.0.0.1:8080/api"
            },
            {
                "label": "Custom Header",
                "name": "header_list",
                "type": "kv_list",
                "default": "[]",
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
        "configurable": True,
        "id": "text_area_input",
        "configuration_template": "text_area_config.html",
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

# Screen widgets are used to parse the output of the various automations and input_forms created in aframe.
# These are by nature tightly tied to the output of the various automations.
# I.E. you will write an screen widget to display the output of some REST API call.
# Configuration:
# label: Human friendly name shown when you want to add non-transient widgets to a 'screen'
# configurable: boolean that determines if this widgets requires some configuration on a per-instance basis
# id: id of the widget
# configuration_template: name of the html template to render for per-instance configuration
# render_template: html template to be rendered on the screen
# consumes_input_form: an input form that can be used for per instance configuration
# transient: allows the widget to be placed and saved on the screen. Transient widgets much be summoned manually
# consumes_automation: the automation to be executed before the widget is rendered. The output of the template is
#   added to the context
SCREEN_WIDGETS = (
    {
        "label": "Menu",
        "configurable": True,
        "id": "menu",
        "configuration_template": "menu_config.html",
        "render_template": "menu.html"
    },
    {
        "label": "Global Menu",
        "configurable": True,
        "id": "global_menu",
        "configuration_template": "global_menu_config.html",
        "render_template": "global_menu.html"
    },
    {
        "label": "Static Image",
        "configurable": True,
        "id": "static_image",
        "configuration_template": "static_image_config.html",
        "render_template": "static_image.html"
    },
    {
        "label": "Open-NTI Graph",
        "configurable": True,
        "id": "opennti_graph",
        "configuration_template": "opennti_graph_config.html",
        "render_template": "static_image.html",
        "consumes_input_form": "grafana_interfaces_graph_url"
    },
    {
        "label": "Network Topology",
        "configurable": False,
        "id": "network_topology",
        "render_template": "network_topology.html"
    },
    {
        "label": "Minion Status",
        "configurable": False,
        "transient": True,
        "id": "minion_status",
        "render_template": "salt_minion_status.html",
        "consumes_automation": "get_salt_minion_status"
    },
    {
        "label": "Proxy List",
        "configurable": False,
        "transient": False,
        "id": "minion_list",
        "render_template": "salt_proxy_list.html",
        "consumes_automation": "get_salt_proxy_list"
    },
    {
        "label": "Minion Config",
        "configurable": False,
        "transient": True,
        "id": "minion_config",
        "render_template": "salt_minion_config.html",
        "consumes_automation": "get_salt_minion_config"
    },
    {
        "label": "Open-NTI Graph",
        "configurable": False,
        "transient": True,
        "id": "opennti_inline_graph",
        "render_template": "static_image.html",
        "consumes_automation": "grafana_all_interfaces_graph_url"
    },
    {
        "label": "Simple List",
        "configurable": True,
        "configuration_template": "list_config.html",
        "id": "simple_list",
        "render_template": "list.html"
    },
    {
        "label": "Raw HTML",
        "configurable": True,
        "configuration_template": "html_config.html",
        "id": "html_contents",
        "render_template": "html.html"
    }
)
