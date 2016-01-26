import abc
from a_frame.utils.endpoint_providers.endpoint_base import EndpointBase


class StaticDiscovery(EndpointBase):
    """
        example endpoint list provider. Simply gets
        configured with a static list in the projects settings.py file

        Example settings:
        DEVICE_DISCOVERY_PROVIDER = (
                {
                    'name': 'FileEndpointList',
                    'data': 'endpointList.txt',
                },
                {
                    'name': 'StaticDiscovery',
                    'data': [
                        ['1', 'pit-spr-05-001', '10.1.5.1', 'admin', 'Clouds123', 'acx1000'],
                        ['2', 'pit-spr-05-001', '10.1.5.1', 'admin', 'Clouds123', 'acx1000'],
                        ['3', 'pit-spr-05-001', '10.1.5.1', 'admin', 'Clouds123', 'acx2200'],
                        ['4', 'pit-spr-05-001', '10.1.5.1', 'admin', 'Clouds123', 'acx2200'],
                    ]
                }

        This is only really useful for demonstration purposes
    """

    iterator = ""

    def load(self, endpoint_list):
        # create the required iterator from the endpoint_list
        self.iterator = iter(endpoint_list)
        return

    def get_next(self):
        # grab the next array from the iterator
        endpoint_array = self.iterator.next()
        # use the base class create_endpoint method to generate the endpoint pyobject
        return self.create_endpoint(*endpoint_array)

