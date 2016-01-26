"""
    module to provide a list of endpoint providers
    endpoint providers are bits of python code
"""

from a_frame.utils.endpoint_providers.endpoint_base import EndpointBase

from a_frame import settings
import importlib

for class_config in settings.DEVICE_DISCOVERY_PROVIDERS:
    print "importing module_name: %s" % class_config['name']
    m = importlib.import_module("a_frame.utils.endpoint_providers." + class_config['name'])
    print "loading class"
    c = getattr(m, class_config["name"])


def get_endpoint_discovery_provider_list():
    provider_list = []
    for sc in EndpointBase.__subclasses__():
        if sc.__name__ is not None:
            print sc.__name__
            provider_list.append(sc.__name__)

    return provider_list


def get_provider_instance(provider_name):
    for config in settings.DEVICE_DISCOVERY_PROVIDERS:
        if config["name"] == provider_name:
            module = importlib.import_module("a_frame.utils.endpoint_providers." + config['name'])
            class_object = getattr(module, config["name"])
            class_instance = class_object()
            class_instance.load(config["data"])
            class_instance.label = config["label"]
            return class_instance

