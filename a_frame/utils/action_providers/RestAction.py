import base64
import json
import platform
import ssl
import urllib2
from urllib2 import HTTPError
from lxml import etree
from a_frame.utils.action_providers.action_base import ActionBase


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
    host = "127.0.0.1:8080"
    request_type = "GET"
    content_type = "application/json"
    accepts_type = "application/json"

    _keystone_auth_path = ":5000/v3/auth/tokens"
    _oauth2_auth_path = "/oauth2/token"
    _auth_token = ""
    _ruckus_auth_path = "/v3_1/session"

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

        full_url = self.protocol + "://" + self.host + self.url
        print full_url

        request = urllib2.Request(full_url)
        
        if self.auth_type == "basic":
            print "using username: %s" % self.username
            base64string = base64.b64encode("%s:%s" % (self.username, self.password))
            request.add_header("Authorization", "Basic %s" % base64string)

        elif self.auth_type == "keystone":
            if not self.connect_to_keystone():
                return "Authentication error connecting to Keystone!"

            print "Connected to Keystone!"
            request.add_header("X-Auth-Token", self._auth_token)

        elif self.auth_type == "oauth2":
            if not self.connect_to_oauth2():
                return "Authentication error!"

            print "OAuth2 authentication succeeded!"
            request.add_header("Authorization", str(self._auth_token))

        elif self.auth_type == "ruckus":
            if not self.connect_to_ruckus():
                return "Authentication error!"

            print "Ruckus authentication succeeded!"
            request.add_header("Cookie", "JSESSIONID=" + str(self._auth_token))

        request.get_method = lambda: self.request_type

        if self.accepts_type != "":
            request.add_header("Accept", self.accepts_type)

        data = str(template + "\n\n")
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

    def connect_to_oauth2(self):
        """
        connects to OAuth2 with the specified user and password

        :return: boolean if successful

        """

        _auth_json = """
            { "grant_type": "password",
              "username": "%s",
              "password": "%s"
            }
            """ % (self.username, self.password)

        full_url = self.protocol + "://" + self.host + self._oauth2_auth_path
        print full_url
        request = urllib2.Request(full_url)

        print "OAuth2 using username/password: %s %s" % (self.username, self.password)
        base64string = base64.b64encode("%s:%s" % (self.username, self.password))
        request.add_header("Authorization", "Basic %s" % base64string)
        request.add_header("Content-Type", "application/json")

        if hasattr(ssl, 'SSLContext'):
            context = ssl.create_default_context()  # disables SSL cert checking!
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            result = urllib2.urlopen(request, _auth_json, context=context).read()
        else:
            result = urllib2.urlopen(request, _auth_json).read()

        try:
            json_string = json.loads(result)
            print "Found OAuth2 JSON result"
        except ValueError:
            print "Unknown OAuth2 result!"
            return False

        if not json_string["token_type"] or not json_string["access_token"]:
            return False

        self._auth_token = json_string["token_type"] + " " + json_string["access_token"]
        return True

    def connect_to_ruckus(self):
        """
        connects to Ruckus REST server to get a Cookie with the specified user and password

        :return: boolean if successful

        """

        _auth_json = """
           {
            "username" : "%s",
            "password" : "%s"
            }
            """ % (self.username, self.password)

        full_url = self.protocol + "://" + self.host + self._ruckus_auth_path
        print full_url
        request = urllib2.Request(full_url)

        print "Ruckus Rest Cookie using username/password: %s %s" % (self.username, self.password)
        request.add_header("Content-Type", "application/json")

        if hasattr(ssl, 'SSLContext'):
            context = ssl.create_default_context()  # disables SSL cert checking!
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            result = urllib2.urlopen(request, _auth_json, context=context).read()
        else:
            result = urllib2.urlopen(request, _auth_json).read()

        auth_token_string = result.info().getheader('Set-cookie')
        self._auth_token = auth_token_string.split(';')[0]

        return True

