import abc
from a_frame.utils.endpoint_providers.endpoint_base import EndpointBase
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

    def load(self, data):
        """
        Attempt to load the results from the cache. If no cache exists, run a new scan and cache those results
        :param data: configuration data from the settings.py file
        :return: None
        """
        global results, config_data
        self.config_data = data

        # remove '/' from network name so we can use it for our cache
        cache_network_name = data["network"].replace('/', '-')
        cache_key_name = 'NmapDiscovery_%s' % cache_network_name

        # query the cache
        results = cache.get(cache_key_name)

        if results is None:
            print "No results found - performing new scan"
            ps = PortScanner()
            results = ps.scan(hosts=data["network"], arguments='-sP')
            cache.set(cache_key_name, results, data["cache_timeout"])

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
                'id': id,
                'name': name,
                'ip': ip,
                'username': username,
                'password': password,
                'type': endpoint_type
            }
        """
        (id, data) = results_object
        if len(data["hostnames"]) > 0:
            name = data["hostnames"][0]["name"]
        else:
            name = id

        username = self.config_data["username"]
        password = self.config_data["password"]
        endpoint_type = self.config_data["endpoint_type"]

        ip = data["addresses"]["ipv4"]

        endpoint_data = {
            'id': id,
            'name': name,
            'ip': ip,
            'username': username,
            'password': password,
            'type': endpoint_type
        }
        return endpoint_data

    def get_endpoint_by_id(self, endpoint_ip):
        """
        for NmapDiscovery, id is always == to endpoint_ip
        run a new scan only on that ip. Ignores cache
        :param endpoint_ip:
        :return: endpoint pyobject
        """
        ps = PortScanner()
        r = ps.scan(hosts=endpoint_ip, arguments='-sP')
        print r
        return self.create_endpoint((endpoint_ip, r["scan"][endpoint_ip]))

    def __del__(self):
        cache.delete('NmapDiscovery-%s' % self.config_data["network"])


