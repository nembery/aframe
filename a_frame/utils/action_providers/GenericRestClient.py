import abc
from a_frame.utils.action_providers.action_base import ActionBase
from lxml import etree
import urllib2
import base64


class GenericRestClient(ActionBase):
    """
        Simple REST action provider

        This is a 'standalone' action, meaning it will be executed without an endpoint being passed in
    """

    # inherited set_global_options from action_base.py will overwrite all of these automatically from the
    # 'create_template' selections
    auth_type = "none"
    username = 'demo'
    password = 'demo'
    url = 'https://127.0.0.1/api/space/device-management/devices'
    request_type = "GET"
    content_type = "application/json"

    def execute_template(self, template):
        """
        We now have the global config (if any), the instance config, and the completed template from the input_form
        and can perform the desired request

        :return Boolean based on execution outcome.
        """
        print "executing %s" % template

        request = urllib2.Request(self.url)
        if self.auth_type == "basic":
            # fixme - add keystone auth here
            print "using username: %s" % self.username
            base64string = base64.encodestring('%s:%s' % (self.username, self.password))
            request.add_header("Authorization", "Basic %s" % base64string)

        request.get_method = lambda: self.request_type
        request.add_header("Content-Type", self.content_type)

        if self.request_type == "GET" or self.request_type == "DELETE":
            try:
                r = urllib2.urlopen(request)
                results = r.read()

                # use pretty_print if we have an xml document returned
                if results.startswith("<?xml"):
                    xml = etree.fromstring(results)
                    return etree.tostring(xml, pretty_print=True)

                # otherwise, just return what we have
                return results
            except Exception as ex:
                print str(ex)
                return "Error!"
        else:
            return urllib2.urlopen(request, template)

