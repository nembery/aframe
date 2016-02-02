import abc
from endpoint_base import EndpointBase
from django.core.cache import cache
from nmap.nmap import PortScanner


class NmapDiscovery(EndpointBase):
    """
        Will use nmap to discover hosts in the given network range
        It is expected you know what these endpoints are, so you must manually configure
        the type and access information in the settings file

        results will be cached if cache_timeout > 0

    """
    iterator = None
    config_data = None

    def get_config_options(self):
        config = [
            {
                "name": "network",
                "label": "Network CIDR",
                "type": "text",
                "value": "10.0.1.0/24"
            },
            {
                "name": "username",
                "label": "Username",
                "type": "text",
                "value": "root"
            },
            {
                "name": "password",
                "label": "Password",
                "type": "text",
                "value": "Clouds123"
            },
            {
                "name": "endpoint_type",
                "label": "Endpoint type",
                "type": "text",
                "value": "junos"
            },
            {
                "name": "cache_timeout",
                "label": "Cache Results (seconds)",
                "type": "text",
                "value": "180"
            }
        ]
        return config

    def load_instance_config(self, config):
        """
        Attempt to load the results from the cache. If no cache exists, run a new scan and cache those results
        :param data: configuration data from the settings.py file
        :return: None
        """
        global results

        # remove "/" from network name so we can use it for our cache
        cache_network_name = self.get_config_value("network").replace("/", "-")
        cache_key_name = "NmapDiscovery_%s" % cache_network_name

        # query the cache
        results = cache.get(cache_key_name)

        if results is None:
            print "No results found - performing new scan"
            ps = PortScanner()
            results = ps.scan(hosts=self.get_config_value("network"), arguments="-sP")
            cache.set(cache_key_name, results, int(self.get_config_value("cache_timeout")))

        self.iterator = iter(results["scan"].iteritems())
        return

    def get_next(self):
        # grab the next array from the iterator
        results_object = self.iterator.next()
        # use the base class create_endpoint method to generate the endpoint pyobject
        return self.create_endpoint(results_object)

    def create_endpoint(self, results_object):
        """
            create the endpoint object from the results we get from NMap
            endpoint_data = {
                "id": id,
                "name": name,
                "ip": ip,
                "username": username,
                "password": password,
                "type": endpoint_type
            }
        """
        (id, data) = results_object
        if len(data["hostnames"]) > 0:
            name = data["hostnames"][0]["name"]
        else:
            name = id

        username = self.get_config_value("username")
        password = self.get_config_value("password")
        endpoint_type = self.get_config_value("endpoint_type")

        ip = data["addresses"]["ipv4"]

        endpoint_data = {
            "id": id,
            "name": name,
            "ip": ip,
            "username": username,
            "password": password,
            "type": endpoint_type
        }
        return endpoint_data

    def get_endpoint_by_id(self, endpoint_ip):
        """
        for NmapDiscovery, id is always == endpoint_ip
        run a new scan only on that ip. Ignores cache
        :param endpoint_ip:
        :return: endpoint pyobject
        """
        ps = PortScanner()
        r = ps.scan(hosts=endpoint_ip, arguments="-sP")
        print r
        return self.create_endpoint((endpoint_ip, r["scan"][endpoint_ip]))

    def __del__(self):
        cache.delete("NmapDiscovery_%s" % self.get_config_value("network").replace("/", "-"))



