import abc
from a_frame.utils.action_providers.action_base import ActionBase
from lxml import etree
import urllib2
import base64


class JunosSpaceRestClient(ActionBase):
    """
        rest client for junos space

        This is a 'standalone' action, meaning it will be executed without an endpoint being passed in
    """

    # inherited set_global_options from action_base.py will overwrite all of these automatically
    username = 'demo'
    password = 'demo'
    url = 'api/space/device-management/devices'
    request_type = "GET"
    ip = '1.1.1.1'
    content_type = "application/json"
    protocol = 'https'

    def execute_template(self, template):
        """
        We now have the global config (if any), the instance config, and the completed template from the input_form
        and can perform the desired request

        :return Boolean based on execution outcome.
        """
        print "executing %s" % template

        # silly validation check
        if "://" not in self.protocol:
            self.protocol += "://"

        destination_url = self.protocol + self.ip + self.url
        print destination_url
        request = urllib2.Request(destination_url)
        print "using username: %s" % self.username
        base64string = base64.encodestring('%s:%s' % (self.username, self.password))
        request.add_header("Authorization", "Basic %s" % base64string)
        # request.add_header('Content-Type', 'text/plain')
        request.get_method = lambda: self.request_type
        if self.request_type == "GET":
            print str(request)
            print "issuing GET"
            try:
                r = urllib2.urlopen(request)
                results = r.read()

                # pretty up if we have an xml document returned
                if results.startswith("<?xml"):
                    xml = etree.fromstring(results)
                    return etree.tostring(xml, pretty_print=True)

                # otherwise, just return what we have
                return results
            except Exception as ex:
                print str(ex)
                return "Error!"
        else:
            print self.request_type
            request.add_header("Content-Type", self.content_type)
            return urllib2.urlopen(request, template)


