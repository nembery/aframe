"""
    module to provide a list of endpoint providers
    endpoint providers are bits of python code
"""

from a_frame.utils.action_providers.action_base import ActionBase

from a_frame import settings
import importlib


def get_action_provider_list():
    provider_list = []
    for c in settings.ACTION_PROVIDERS:
        provider_list.append(c["label"])

    return provider_list


def get_action_provider_select():
    provider_list = list()
    provider_list.append(("n/a", "Please select an action"))
    for c in settings.ACTION_PROVIDERS:
        print(c)
        provider_list.append((c["name"], c["label"]))

    return provider_list


def get_provider_instance(provider_name, options):
    for config in settings.ACTION_PROVIDERS:
        if config["name"] == provider_name:
            print("loading %s" % provider_name)
            module = importlib.import_module("a_frame.utils.action_providers." + config["class"])
            class_object = getattr(module, config["class"])
            class_instance = class_object()
            if "global" in config:
                class_instance.set_global_options(config["global"])

            class_instance.set_instance_options(options)
            print(class_instance)
            return class_instance

    print("COULDN'T FIND IT")
    return None


def get_options_for_provider(provider_name):
    for a in settings.ACTION_PROVIDERS:
        if a["name"] == provider_name:
            return a["options"]
