import json
import ssl
import urllib2

from endpoint_base import EndpointBase
from django.core.cache import cache


class SaltMinion(EndpointBase):
    """
        Connects to a salt master via the cherrypy rest API

        Will cache the results for configurable amount of time

    """
    iterator = None
    config = ""
    username = ""
    password = ""
    host = ""
    protocol = "http"
    cache_timeout = "10"

    offset = 0
    paging_size = 10
    counter = 0
    _saltapi_auth_path = "/login"

    def get_config_options(self):
        config = [
            {
                "name": "host",
                "label": "Salt Master IP and API Port",
                "type": "text",
                "value": "0.0.0.0:8000"
            },
            {
                "name": "username",
                "label": "Username",
                "type": "text",
                "value": "juniper"
            },
            {
                "name": "password",
                "label": "Password",
                "type": "text",
                "value": "Clouds123"
            },
            {
                "name": "protocol",
                "label": "Protocol",
                "type": "select",
                "value": "http",
                "choices": [
                    {
                        "name": "http",
                        "label": "http"
                    },
                    {
                        "name": "https",
                        "label": "https"
                    }
                ]
            },
            {
                "name": "cache_timeout",
                "label": "Cache Timeout",
                "type": "select",
                "value": "10",
                "choices": [
                    {
                        "name": "10",
                        "label": "10 Seconds"
                    },
                    {
                        "name": "30",
                        "label": "30 Seconds"
                    },
                    {
                        "name": "60",
                        "label": "60 Seconds"
                    },
                    {
                        "name": "180",
                        "label": "180 Seconds"
                    },
                    {
                        "name": "300",
                        "label": "300 Seconds"
                    }
                ]
            }
        ]
        return config

    def load_instance_config(self, config):
        """
        set the configuration on the object
        :param config: the configuration from the endpoint group settings
        """
        self.username = self.get_config_value("username")
        self.password = self.get_config_value("password")
        self.host = self.get_config_value("host")
        self.protocol = self.get_config_value("protocol")

        self.load_iterator()
        return None

    def get_next(self):
        global counter
        if self.counter < self.paging_size:
            self.counter += 1
            # grab the next array from the iterator
        else:
            self.increment_offset()

        n = self.iterator.next()
        return self.create_endpoint(n)

    def create_endpoint(self, d):
        """
            create the endpoint object from the results we get from Salt
            endpoint_data = {
                "id": id,
                "name": name,
                "ip": ip,
                "username": username,
                "password": password,
                "type": endpoint_type
            }
        """
        print "ID IS"
        print d
        device_id = str(d["id"])
        if 'hostname' in d:
            name = str(d['hostname'])
        elif 'junos_facts' in d and 'hostname' in d['junos_facts']:
            name = str(d['junos_facts']['hostname'])
        else:
            name = str(d["nodename"])
        if "fqdn_ip4" in d:
            ip = str(d["fqdn_ip4"][0])
        elif 'host' in d:
            ip = str(d['host'])
        else:
            ip = '0.0.0.0'

        print "GOT EVERYTHING HERE"
        # do not override default username / password
        username = ""
        password = ""

        # FIXME - maybe this needs to be os_family or some other variant?
        endpoint_type = str(d["os"])

        endpoint_data = {
            "id": device_id,
            "name": name,
            "ip": ip,
            "username": username,
            "password": password,
            "type": endpoint_type
        }
        return endpoint_data

    def get_endpoint_by_id(self, endpoint_id):

        url = "/minions/%s" % endpoint_id
        r = self.query_url(url)

        jr = json.loads(r)

        print jr

        device = jr["return"][0][endpoint_id]

        return self.create_endpoint(device)

    def load_iterator(self):

        global counter
        global offset

        # reset counter to 0 since we just grabbed a new list of devices from the Salt API server
        self.counter = 0

        url = "/minions"

        cache_key_name = "salt_minion_%s" % self.host

        # query the cache
        results = cache.get(cache_key_name)

        if results is None:
            print "No results found - performing new query"
            results = list()

            r = self.query_url(url)
            if r is None:
                self.iterator = iter(results)
                return

            jr = json.loads(r)
            if 'return' not in jr:
                self.iterator = iter(results)
                return

            for d in jr["return"][0]:
                print "appending results"
                if jr["return"][0][d]:
                    results.append(jr["return"][0][d])

            cache.set(cache_key_name, results, int(self.get_config_value("cache_timeout")))

        self.iterator = iter(results)

        # increase the offset as well
        self.offset += self.paging_size

    def query_url(self,url):
        try:
            full_url = self.protocol + "://" + self.host + url

            print full_url

            self.__connect_to_saltapi()

            request = urllib2.Request(full_url)
            request.add_header("X-Auth-Token", str(self._auth_token))

            return self.__perform_get(request)
        except IOError:
            print "Could not connect to endpoint provider! Caught IOError"
            return None
        except Exception as e:
            print repr(e)
            print "Could not connect to endpoint provider!"
            return None

    @staticmethod
    def __perform_post(request, data):
        if hasattr(ssl, 'SSLContext'):
            context = ssl.create_default_context()  # disables SSL cert checking!
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            return urllib2.urlopen(request, data, context=context)

        else:
            print "no ssl"
            return urllib2.urlopen(request, data)

    @staticmethod
    def __perform_get(request):
        if hasattr(ssl, 'SSLContext'):
            context = ssl.create_default_context()  # disables SSL cert checking!
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            return urllib2.urlopen(request, context=context).read()
        else:
            return urllib2.urlopen(request).read()

    def __connect_to_saltapi(self):
        """
        connects to salt api endpoint to get a token with the specified user and password

        defaults to 'pam' eauth method

        :return: boolean if successful

        """

        _auth_json = """
               {
                "username" : "%s",
                "password" : "%s",
                "eauth": "pam"
                }
                """ % (self.username, self.password)

        if ':' not in self.host:
            # if we don't have a port specified, let's add the default of 8000 here
            self.host += ':8000'

        full_url = self.protocol + "://" + self.host + self._saltapi_auth_path
        request = urllib2.Request(full_url)

        print "Authenticating to salt-api with username/password: %s %s" % (self.username, self.password)
        request.add_header("Content-Type", "application/json")

        result = self.__perform_post(request, _auth_json).read()
        json_results = json.loads(result)
        self._auth_token = json_results['return'][0]['token']

        return True
