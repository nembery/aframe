import abc
from endpoint_base import EndpointBase
from django.core.cache import cache
import urllib2
import urllib
import base64
import ssl
from lxml import etree


class JunosSpaceDeviceList(EndpointBase):
    """
        Connects to a junos space instance

    """
    iterator = None
    config = ""
    request = ""
    username = ""
    password = ""
    host = ""

    offset = 0
    paging_size = 10
    counter = 0

    def get_config_options(self):
        config = [
            {
                "name": "host",
                "label": "Space Host IP address",
                "type": "text",
                "value": "0.0.0.0"
            },
            {
                "name": "username",
                "label": "Username",
                "type": "text",
                "value": "super"
            },
            {
                "name": "password",
                "label": "Password",
                "type": "text",
                "value": "abc123"
            },
        ]
        return config

    def load_instance_config(self, config):
        """
        set the configuration on the object
        :param instance_config: the configuration from the endpoint group settings
        """
        self.username = self.get_config_value("username")
        self.password = self.get_config_value("password")
        self.host = self.get_config_value("host")

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
        device_id = d.get('key')
        if device_id is None:
            device_id = d.find('./id').text

        # skip creation if device is down
        if d.find('./connectionStatus') is not None:
            # different XML location for status in device list
            connection_status =  d.find('./connectionStatus').text
        else:
            # vs by device_id
            connection_status = d.find('./connection-status/status').text
        if connection_status != 'up':
            return

        name = d.find('./name').text
        ip = d.find('./ipAddr').text
        username = ""
        password = ""
        endpoint_type = d.find('./platform').text

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

        url = "/api/space/device-management/devices/%s" % endpoint_id
        xml = self.query_url(url)
        device = etree.fromstring(xml)
        return self.create_endpoint(device)

    def load_iterator(self):

        global request
        global counter
        global offset

        # reset counter to 0 since we just grabbed a new list of devices from the Space server
        self.counter = 0

        params = {'paging': '(start eq %s,limit eq %s )' % (self.offset, self.paging_size)}
        p = urllib.urlencode(params)

        url = "/api/space/device-management/devices?%s" % p

        xml = self.query_url(url)

        doc = etree.fromstring(xml)
        self.iterator = iter(doc.findall('./device'))

        # increase the offset as well
        self.offset += self.paging_size

    def query_url(self,url):
        full_url = "https://" + self.host + url

        print full_url

        r = urllib2.Request(full_url)

        base64string = base64.b64encode("%s:%s" % (self.username, self.password))
        r.add_header("Authorization", "Basic %s" % base64string)
        r.get_method = lambda: "GET"

        if hasattr(ssl, 'SSLContext'):
            context = ssl.create_default_context()  # disables SSL cert checking!
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            xml = urllib2.urlopen(r, context=context).read()
        else:
            xml = urllib2.urlopen(r).read()

        print xml
        return xml
