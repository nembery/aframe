"""
    module to provide a list of endpoint providers
    endpoint providers are bits of python code
"""

from endpoints.plugins.endpoint_base import EndpointBase
from models import EndpointGroup
from a_frame import settings
import importlib
import json

for class_config in settings.REGISTERED_ENDPOINT_PROVIDERS:
    print "importing module_name: %s" % class_config["name"]
    m = importlib.import_module("endpoints.plugins." + class_config["class"])
    print "loading class"
    c = getattr(m, class_config["class"])


def get_endpoint_discovery_provider_list():
    return settings.REGISTERED_ENDPOINT_PROVIDERS


def get_endpoint_discovery_provider_list_old():
    provider_list = []

    for sc in EndpointBase.__subclasses__():
        if sc.__name__ is not None:
            print sc.__name__
            provider_list.append(sc.__name__)

    return provider_list


def get_provider_instance(provider_class):
    print EndpointBase.__subclasses__()
    for sc in EndpointBase.__subclasses__():
        if sc.__name__ == provider_class:
            return sc()


def get_provider_instance_from_group(group_id):
    """
    :param group_id: id of the Endpoint Group
    :return: Provider instance with the end point group configuration applied
    """
    group = EndpointGroup.objects.get(pk=group_id)
    print "GO"
    # get the right provider instance
    provider_instance = get_provider_instance(group.provider_class)

    print provider_instance
    # convert json encoded config to a python object
    config = json.loads(group.provider_configuration)

    # save and load config into this provider instance
    provider_instance.set_instance_config(config)

    return provider_instance
