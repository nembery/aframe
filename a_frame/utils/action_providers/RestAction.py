import abc
from a_frame.utils.action_providers.action_base import ActionBase
from lxml import etree
import urllib2
import base64
import platform
import json
import ssl
from urllib2 import HTTPError


class RestAction(ActionBase):
    """
        Simple REST action provider

        This is a "standalone" action, meaning it will be executed without an endpoint being passed in
    """

    # inherited set_global_options from action_base.py will overwrite all of these automatically from the
    # "create_template" selections
    auth_type = "none"
    keystone_host = "127.0.0.1"
    keystone_project = "admin"
    username = "demo"
    password = "demo"
    url = "/api/space/device-management/devices"
    protocol = "https"
    host = "127.0.0.1"
    request_type = "GET"
    content_type = "application/json"
    accepts_type = "application/json"

    _keystone_auth_path = ":5000/v3/auth/tokens"
    _auth_token = ""

    def execute_template(self, template):
        """
        We now have the global config (if any), the instance config, and the completed template from the input_form
        and can perform the desired request
        :param template: the completed template from the user or API
        :return Boolean based on execution outcome.
        """
        # print "executing %s" % template

        if not self.url.startswith(':') and not self.url.startswith('/'):
            self.url = "/" + self.url

        # set up debugging output
        handler = urllib2.HTTPHandler(debuglevel=1)
        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)

        # ensure no CRLF has snuck through
        template = template.replace('\r\n', '\n')

        request = urllib2.Request(self.protocol + "://" + self.host + self.url)
        if self.auth_type == "basic":
            print "using username: %s" % self.username
            base64string = base64.b64encode("%s:%s" % (self.username, self.password))
            request.add_header("Authorization", "Basic %s" % base64string)
        elif self.auth_type == "keystone":
            if not self.connect_to_keystone():
                return "Authentication error connecting to Keystone!"

            print "Connected to Keystone!"
            request.add_header("X-Auth-Token", self._auth_token)

        request.get_method = lambda: self.request_type
        # request.add_header("Accept", self.accepts_type)

        print self.accepts_type
        print self.content_type

        data = template + "\n\n"
        print "Request type: %s" % self.request_type

        if self.request_type == "GET" or self.request_type == "DELETE":
            try:
                if hasattr(ssl, 'SSLContext'):
                    context = ssl.create_default_context()  # disables SSL cert checking!
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    r = urllib2.urlopen(request, context=context)
                else:
                    r = urllib2.urlopen(request)
                results = r.read()
                return self.format_results(results)

            except Exception as ex:
                print str(ex)
                return "Error! %s" % str(ex)
        else:
            # this is a POST attempt
            try:
                request.add_header("Content-Type", self.content_type)
                request.add_header("Content-Length", len(data))
                if hasattr(ssl, 'SSLContext'):
                    context = ssl.create_default_context()  # disables SSL cert checking!
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    results = urllib2.urlopen(request, data, context=context).read()
                else:
                    results = urllib2.urlopen(request, data).read()
                return self.format_results(results)
            except HTTPError as he:
                return "Error! %s" % str(he)

    @staticmethod
    def format_results(results):
        """
        detects string format (xml || json) and formats appropriately

        :param results: string from urlopen
        :return: formatted string output
        """
        # use pretty_print if we have an xml document returned
        if results.startswith("<?xml"):
            print "Found XML results - using pretty_print"
            print results
            xml = etree.fromstring(results)
            return etree.tostring(xml, pretty_print=True)

        # is the result valid json?
        try:
            json_string = json.loads(results)
            print "Found JSON results"
            return json.dumps(json_string, indent=4)
        except ValueError:
            # this isn't xml or json, so just return it!
            print "Unknown results!"
            return results

    def connect_to_keystone(self):
        """
        connects to Keystone in the specified project scope

        :return: boolean if successful

        """

        _auth_json = """
            { "auth": {
                "identity": {
                  "methods": ["password"],
                  "password": {
                    "user": {
                      "name": "%s",
                      "domain": { "id": "default" },
                      "password": "%s"
                    }
                  }
                },
                  "scope": {
                        "project": {
                            "domain": {
                                "id": "default"
                            },
                            "name": "%s"
                        }
                    }
                }
            }
            """ % (self.username, self.password, self.keystone_project)

        full_url = "http://" + self.keystone_host + self._keystone_auth_path
        print full_url
        request = urllib2.Request(full_url)
        request.add_header("Content-Type", "application/json")
        request.add_header("charset", "UTF-8")
        request.add_header("X-AFrame-Useragent", "%s:%s" % (platform.node(), "aframe_rest_client"))
        request.add_header("Content-Length", len(_auth_json))
        result = urllib2.urlopen(request, _auth_json)
        self._auth_token = result.info().getheader('X-Subject-Token')
        return True
