import abc
from endpoint_base import EndpointBase


class StaticList(EndpointBase):
    """
    Example endpoint provider that simply defines a static list as part of it"s configuration

    get_config_options uses a "list" type with the list items each describing an endpoint. The UI
    will allow the user to add multiple items to the configuration thus allowing a static list of endpoints
    """

    iterator = ""

    def get_config_options(self):
        config = [
            {
                "name": "endpoint_list",
                "type": "list",
                "label": "Endpoint List",
                "value": "[]",
                "list_items": [
                    {
                        "name": "id",
                        "label": "ID",
                        "value": "0"
                    },
                    {
                        "name": "name",
                        "label": "Name",
                        "value": "example name"
                    },
                    {
                        "name": "ip",
                        "label": "IPv4 Address",
                        "value": "1.1.1.1"
                    },
                    {
                        "name": "username",
                        "label": "Username",
                        "value": "root"
                    },
                    {
                        "name": "password",
                        "label": "Password",
                        "value": "pw123"
                    },
                    {
                        "name": "type",
                        "label": "Type",
                        "value": "junos"
                    },
                ]
            }
        ]
        return config

    def load_instance_config(self, config):
        endpoint_list_json = self.get_config_value("endpoint_list")
        # create the required iterator from the endpoint_list
        self.iterator = iter(endpoint_list_json)
        return

    def get_next(self):
        # grab the next array from the iterator
        endpoint_array = self.iterator.next()
        # use the base class create_endpoint method to generate the endpoint pyobject

        endpoint = {}
        for i in endpoint_array:
            print i
            endpoint[i] = endpoint_array[i]

        return endpoint


