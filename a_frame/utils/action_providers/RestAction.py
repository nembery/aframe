import base64
import json
import platform
import re
import ssl
import urllib
import urllib2
import uuid
from urllib2 import HTTPError

from django.core.cache import cache
from lxml import etree

from a_frame.utils.action_providers.action_base import ActionBase


class RestAction(ActionBase):
    """
        Simple REST action provider

        This is a "standalone" action, meaning it will be executed without an endpoint being passed in

        This will handle GET, POST, and DELETE verbs for REST actions. Multiple authentication schemes are also
        supported.

        For POST operations, the input template will be rendered as-is and used as the data payload
        For GET operations, the input template must be configured as a JSON formatted string. This will be
        converted to a the appropriate query parameters if needed. I.E. if you need something like ?action=create
        added to the end of the URL, add template data as such: { "action": "create" }
    """

    # inherited set_global_options from action_base.py will overwrite all of these automatically from the
    # "create_template" selections
    auth_type = "none"
    keystone_host = "127.0.0.1"
    keystone_project = "admin"
    username = "demo"
    password = "demo"
    url = "/api/"
    protocol = "https"
    host = "127.0.0.1:8080"
    request_type = "GET"
    content_type = "application/json"
    accepts_type = "application/json"
    cache_timeout = 3600
    full_url = ""
    header_list = ""
    _keystone_auth_path = ":5000/v3/auth/tokens"
    _oauth2_auth_path = "/oauth2/token"
    _auth_token = ""
    _ruckus_auth_path = "/v3_1/session"
    _saltapi_auth_path = "/login"

    def execute_template(self, template):
        """
        We now have the global config (if any), the instance config, and the completed template from the input_form
        and can perform the desired request
        :param template: the completed template from the user or API
        :return Boolean based on execution outcome.
        """
        print("executing %s" % template)

        if not self.url.startswith(':') and not self.url.startswith('/'):
            self.url = "/" + self.url

        # set up debugging output
        handler = urllib2.HTTPHandler(debuglevel=1)
        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)

        # ensure no CRLF was able to snick through
        template = template.replace('\r\n', '\n')

        # basic Rest Action allows the user to configure the full_url withouth host, protocol and url broken out
        if self.full_url == "":
            full_url = self.protocol + "://" + self.host + self.url
        else:
            full_url = self.full_url

        if self.request_type == "GET" and template != '':
            print(template)
            ct = self.unescape(template)
            print(ct)
            try:
                json_query_params = json.loads(ct)
                query_data = urllib.urlencode(json_query_params)

                if "?" in full_url:
                    full_url += "&"
                else:
                    full_url += "?"

                full_url += query_data
            except ValueError as ve:
                print("Could not parse template data for get request!")
                print(ve)
                pass

        print(full_url)

        request = urllib2.Request(full_url)

        print(self.header_list)

        try:
            if self.header_list != "":
                hl = json.loads(self.header_list)
                for h in hl:
                    if 'key' in h and 'value' in h:
                        print('Adding header: %s' % h['key'])
                        request.add_header(h['key'], h['value'])

        except ValueError:
            print('Could not load headers from string')

        if self.auth_type == "basic":
            print("using username: %s" % self.username)
            base64string = base64.b64encode("%s:%s" % (self.username, self.password))
            request.add_header("Authorization", "Basic %s" % base64string)

        elif self.auth_type == "bearer":
            request.add_header("Authorization", "Bearer %s" % self.password)

        elif self.auth_type == "keystone":
            if not self.__connect_to_keystone():
                return "Authentication error connecting to Keystone!"

            print("Connected to Keystone!")
            request.add_header("X-Auth-Token", self._auth_token)

        elif self.auth_type == "oauth2":
            if not self.__connect_to_oauth2():
                return "Authentication error!"

            print("OAuth2 authentication succeeded!")
            request.add_header("Authorization", str(self._auth_token))

        elif self.auth_type == "ruckus":
            if not self.__connect_to_ruckus():
                return "Authentication error!"

            print("Ruckus authentication succeeded!")
            request.add_header("Cookie", "JSESSIONID=" + str(self._auth_token))

        elif self.auth_type == "saltapi":
            if not self.__connect_to_saltapi():
                return "Authentication error!"

            print("Saltapi authentication succeeded!")
            request.add_header("X-Auth-Token", str(self._auth_token))
            print(self._auth_token)

        request.get_method = lambda: self.request_type

        if self.accepts_type != "":
            request.add_header("Accept", self.accepts_type)

        data = str(template + "\n\n")
        print("Request type: %s" % self.request_type)
        print("%s" % data)

        if self.request_type == "GET" or self.request_type == "DELETE":
            try:
                results_object = self.__perform_get(request)
                if type(results_object) is str:
                    results = results_object
                else:
                    results = results_object.read()

                content_type = results_object.info().getheader('Content-Type')
                print(content_type)
                if results != "":
                    return self.__format_results(results)
                else:
                    return "Successful REST Operation"

            except Exception as ex:
                print(str(ex))
                return "Error! %s" % str(ex)
        else:
            # this is a POST attempt
            try:
                request.add_header("Content-Type", self.content_type)
                request.add_header("Content-Length", len(data))

                result_object = self.__perform_post(request, data)

                if not hasattr(result_object, 'info'):
                    # this is an error string
                    return result_object

                content_type = result_object.info().getheader('Content-Type')
                print('Found content_type of %s' % content_type)

                # check if this is a binary file
                if not re.search('json|text|html|xml', content_type):
                    attachment = result_object.info().getheader('Content-Disposition')
                    print(attachment)
                    print(type(attachment))
                    if attachment is not None and 'filename=' in attachment:
                        print('GOT A FILENAME')
                        filename = attachment.split('filename=')[1]
                        print(filename)
                    else:
                        if 'zip' in content_type:
                            filename = 'aframe_archive.zip'
                        elif 'iso' in content_type:
                            filename = 'aframe_archive.iso'
                        else:
                            filename = 'aframe_archive'

                    # this is a binary response! We can't handle this inline, so let's cache the result
                    # and notify the caller
                    cache_key = str(uuid.uuid4())
                    result = dict()
                    res = result_object.read()
                    # print(res)
                    result['contents'] = res
                    result['display_inline'] = False
                    result['cache_key'] = cache_key

                    cache_object = dict()
                    cache_object['contents'] = res
                    cache_object['filename'] = filename
                    cache_object['content_type'] = content_type
                    cache.set(cache_key, cache_object, self.cache_timeout)
                    return result

                result = result_object.read()

                if result != "":
                    return self.__format_results(result)
                else:
                    return "Successful POST Operation"

            except HTTPError as he:
                return "Error! %s" % str(he)

    def __connect_to_keystone(self):
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
        print(full_url)
        request = urllib2.Request(full_url)
        request.add_header("Content-Type", "application/json")
        request.add_header("charset", "UTF-8")
        request.add_header("X-AFrame-Useragent", "%s:%s" % (platform.node(), "aframe_rest_client"))
        request.add_header("Content-Length", len(_auth_json))

        result = self.__perform_post(request, _auth_json)
        self._auth_token = result.info().getheader('X-Subject-Token')
        return True

    def __connect_to_oauth2(self):
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
        print(full_url)
        request = urllib2.Request(full_url)

        print("OAuth2 using username/password: %s %s" % (self.username, self.password))
        base64string = base64.b64encode("%s:%s" % (self.username, self.password))
        request.add_header("Authorization", "Basic %s" % base64string)
        request.add_header("Content-Type", "application/json")

        result = self.__perform_post(request, _auth_json).read()

        try:
            json_string = json.loads(result)
            print("Found OAuth2 JSON result")
        except ValueError:
            print("Unknown OAuth2 result!")
            return False

        if not json_string["token_type"] or not json_string["access_token"]:
            return False

        self._auth_token = json_string["token_type"] + " " + json_string["access_token"]
        return True

    def __connect_to_ruckus(self):
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
        print(full_url)
        request = urllib2.Request(full_url)

        print("Ruckus Rest Cookie using username/password: %s %s" % (self.username, self.password))
        request.add_header("Content-Type", "application/json")

        result = self.__perform_post(request, _auth_json)

        auth_token_string = result.info().getheader('Set-cookie')
        self._auth_token = auth_token_string.split(';')[0]

        return True

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

        full_url = self.protocol + "://" + self.host + self._saltapi_auth_path
        print(full_url)
        request = urllib2.Request(full_url)

        print("Authenticating to salt-api with username/password: %s %s" % (self.username, self.password))
        request.add_header("Content-Type", "application/json")

        try:
            result_object = self.__perform_post(request, _auth_json)
            # catch the case where the result object is not a valid respone,
            # i.e. an error string or None
            if hasattr(result_object, "read"):
                result = result_object.read()
                json_results = json.loads(result)
                if 'return' in json_results:
                    self._auth_token = json_results['return'][0]['token']
            else:
                print('No valid response!')
                return False

        except HTTPError as he:
            print('Could not auth to salt_api!')
            print(str(he))
            return False
        except ValueError as ve:
            print('Could not parse json results from salt_api')
            print(str(ve))
            return False
        except KeyError:
            print('Could not find valid auth token in salt_api response!')
            print(json_results)
            return False

        return True

    @staticmethod
    def __perform_post(request, data):
        print("PERFORMING POST")
        print(data)
        try:
            if hasattr(ssl, 'SSLContext'):
                context = ssl.create_default_context()  # disables SSL cert checking!
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                return urllib2.urlopen(request, data, context=context)

            else:
                print("no ssl")
                return urllib2.urlopen(request, data)
        except HTTPError as he:
            print("HTTP Error performing get operation")
            return str(he)
        except IOError as io:
            print("IOError performing get operations")
            return str(io)

    @staticmethod
    def __perform_get(request):
        try:
            if hasattr(ssl, 'SSLContext'):
                context = ssl.create_default_context()  # disables SSL cert checking!
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                return urllib2.urlopen(request, context=context)
            else:
                return urllib2.urlopen(request)
        except HTTPError as he:
            print("HTTP Error performing get operation")
            return str(he)
        except IOError as io:
            print("IOError performing get operations")
            return str(io)

    @staticmethod
    def __format_results(results):
        """
        detects string format (xml || json) and formats appropriately

        :param results: string from urlopen
        :return: formatted string output
        """
        if results is None:
            print("no actual results to process")
            return results

        # use pretty_print(if we have an xml document returned)
        try:
            if type(results) == "str" and results.startswith("<?xml"):
                print("Found XML results - using pretty_print")
                print(results)
                xml = etree.fromstring(results)
                return etree.tostring(xml, pretty_print=True)
        except etree.XMLSyntaxError:
            print("Invalid XML response")
            return results

        # is the result valid json?
        try:
            json_string = json.loads(results)
            print("Found JSON results")
            return json.dumps(json_string, indent=4)
        except ValueError:
            # this isn't xml or json, so just return it!
            print("Unknown results!")
            return results
