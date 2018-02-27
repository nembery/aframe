import abc
import re
import netaddr
from netaddr.core import AddrFormatError


class EndpointBase(object):
    """
    Base class for an endpoint provider. To subclass implement these methods:
    get_default_config: Returns an list of configuration dicts in the following format:
    [
        {
            "name": "name of the configuration option",
            "label": "label that the user will see"
            "type": "essentially a widget type. Can be [text|select|list]"
            "value": "default value for text type entries"
            "choices": "list of dict objects with name and label keys"
        },
        {
            "name": "text type example",
            "label": "Example configuration element of type text",
            "type": "text",
            "value": "text_value"
        },
        {
            "name": "select type example",
            "label": "Example select configuration option",
            "type": "select",
            "choices": [
                {
                    "name": "option name 1",
                    "label": "option lable 1"
                },
                {
                    "name": "option name 2",
                    "label": "option label 2"
                }
            ]
        }
    ]
    """
    __metaclass__ = abc.ABCMeta

    default_filters = []
    filter_name = ""
    filter_method = ""
    filter_args = ""
    label = ""
    description = ""
    instance_config = []

    def __init__(self):
        """
            setup default filters
            to add filters in subclasses, append your
            filters to the default_filters array by overriding __init__
        """
        global default_filters
        filters = [
            {
                "name": "Subnet",
                "method": "filter_by_subnet",
                "description": "Returns a list of endpoints within the given subnet",
                "argument_description": "A subnet in CIDR format (1.1.1.0/24)"

            },
            {
                "name": "Name",
                "method": "filter_by_name",
                "description": "Returns a list of endpoints filtered by Name",
                "argument_description": "A regular expression (^vmx\d+$)"
            },
            {
                "name": "Type",
                "method": "filter_by_type",
                "description": "Returns a list of endpoints filtered by Type",
                "argument_description": "A regular expression (^acx2.00$)"
            }
        ]
        self.default_filters = filters

    @abc.abstractmethod
    def get_next(self):
        return

    @abc.abstractmethod
    def load_instance_config(self, config):
        return

    @abc.abstractmethod
    def get_config_options(self):
        return

    def get_endpoint_by_id(self, endpoint_id):
        """
            Although it is not required to override the get_endpoint_by_id function
            it is recommended if your system allows this. otherwise, a default (slow)
            implementation has been provided here
        """
        for endpoint in self:
            print endpoint
            if endpoint["id"] == endpoint_id:
                return endpoint

        return None

    def __iter__(self):
        return self

    def apply_filter(self, filter_name, filter_args):
        global filter_method
        self.filter_name = filter_name
        self.filter_args = filter_args
        for f in self.available_filters():
            if f["name"] == filter_name:
                self.filter_method = f["method"]
                break

        return

    def next(self):
        n = self.get_next()
        r = self.check_endpoint_against_filter(n)
        if r is not None:
            return r
        else:
            return self.next()

    @staticmethod
    def create_endpoint(endpoint_id, endpoint_name, ip, username, password, endpoint_type):
        """
        Returns a basic pyObject representing the most basic information for a endpoint
        feel free to override this to include more specific data members if needed
        :param endpoint_id: unique id
        :param endpoint_name: name
        :param ip: IPv4 address of the endpoint
        :param username: username used to authenticate to the endpoint
        :param password: password used to authenticate to the endpoint
        :param endpoint_type: type of endpoint
        """
        endpoint_data = {
            "id": endpoint_id,
            "name": endpoint_name,
            "ip": ip,
            "username": username,
            "password": password,
            "type": endpoint_type
        }
        return endpoint_data

    def available_filters(self):
        """
        feel free to override the available filters
        if necessary
        """
        return self.default_filters

    def check_endpoint_against_filter(self, endpoint):
        if self.filter_method == "":
            return endpoint

        if hasattr(self, self.filter_method):
            return getattr(self, self.filter_method)(endpoint, self.filter_args)
        else:
            raise Exception("Filter not implemented!")

    @staticmethod
    def filter_by_name(endpoint, substring):
        if re.match(substring, endpoint["name"], re.IGNORECASE):
            return endpoint
        else:
            return None

    @staticmethod
    def filter_by_type(endpoint, substring):
        if re.match(substring, endpoint["type"], re.IGNORECASE):
            return endpoint
        else:
            return None

    @staticmethod
    def filter_by_subnet(endpoint, subnet):
        print "checking %s against subnet" % endpoint["ip"]
        try:
            ip_network = netaddr.IPNetwork(subnet)
        except AddrFormatError:
            print "Bad address format"
            return None
        ip = netaddr.IPAddress(endpoint["ip"])
        if ip in ip_network:
            return endpoint
        else:
            return None

    def get_config_value(self, name):
        """
         Convenience method to search config list and return the value of the
         desired config element

         for config == [{"name": "findme", "value": "righthere" }, {"name": "another", "value": "anotherval" }]
         and name == findme
         returns "righthere"

        :param name: value of the name key to find
        :return: return the value of the "value" key
        """
        for config_element in self.instance_config:
            if config_element["name"] == name:
                return config_element["value"]

    def set_instance_config(self, config):
        """
        saves the instance config to the self.instance_config variable
        then calls the user defined load_instance_config

        :param config: instance configuration object
        :return: None
        """
        self.instance_config = config
        self.load_instance_config(config)

    def get_page(self, offset, page_size):
        results = []
        index = 0
        try:
            while index < offset:
                self.next()
                index += 1

            while len(results) < page_size:
                r = self.next()
                results.append(r)
                print results

            return results

        except StopIteration:
            print "iter stopped"
            print results
            return results




