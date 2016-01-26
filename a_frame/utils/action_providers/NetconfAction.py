import abc
from a_frame.utils.action_providers.action_base import ActionBase
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import *
from lxml import etree
import re


class NetconfAction(ActionBase):
    """
        Uses NetConf to execute the given template

        Can execute template as an op command
        or apply the template as a configuration template
    """

    dev = None
    request_type = "apply_template"

    def set_endpoint(self, endpoint):
        # create the required iterator from the endpoint_list
        self.dev = Device(user=endpoint["username"], password=endpoint["password"], host=endpoint["ip"])
        self.dev.open(gather_facts=False)
        return

    def execute_template(self, template):
        """
        switches based on request_type chosen from template configuration

        :param template:
        :return: String results from the endpoint netconf subsystem
        """
        if self.request_type == "apply_template":
            return self.apply_template(template)
        elif self.request_type == "execute_cheat_command":
            return self.execute_cheat_command(template)
        else:
            return self.execute_op_command(template)

    def execute_op_command(self, template):
        try:
            results = self.dev.execute(template)
        except RpcError as e:
            print e
            return "Error executing command: %s" % str(e)

        print etree.tostring(results, pretty_print=True)
        return etree.tostring(results, pretty_print=True)

    def execute_cheat_command(self, template):
        print "Executing cheat command"
        results = self.dev.cli(template)
        return results

    def assert_configuration(self, template):
        try:
            configuration_xml = self.dev.execute("<get-configuration></get-configuration>")
            print configuration_xml
            if configuration_xml.find(template):
                return "Configuration element: %s is present" % template

            return "Not Found"
        except Exception as e:
            print e

    def apply_template(self, template):
        print self.dev
        results = ""
        conf_string = template.strip()
        # try to determine the format of our config_string
        config_format = 'set'
        if re.search(r'^\s*<.*>$', conf_string, re.MULTILINE):
            config_format = 'xml'
        elif re.search(r'^\s*(set|delete|replace|rename)\s', conf_string):
            config_format = 'set'
        elif re.search(r'^[a-z:]*\s*\w+\s+{', conf_string, re.I) and re.search(r'.*}\s*$', conf_string):
            config_format = 'text'

        print "using format: " + config_format
        cu = Config(self.dev)
        try:
            cu.lock()
        except LockError as le:
            print "Could not lock database!"
            print str(le)
            self.dev.close()
            return False

        try:
            print "loading config"
            cu.load(conf_string, format=config_format)
        except Exception as e:
            print "Could not load configuration"
            print str(e)
            self.dev.close()
            return "Failed, could not load the configuration template"

        diff = cu.diff()
        print diff
        if diff is not None:
            try:
                cu.commit_check()
                print "Committing config!"
                cu.commit(comment="Commit via a_frame")

            except CommitError as ce:
                print "Could not load config!"
                cu.rollback()
                print repr(ce)
                return "Failed, commit check failed"

        else:
            # nothing to commit
            print "Nothing to commit - no diff found"
            return "Nothing to commit!"

        try:
            print "Unlocking database!"
            cu.unlock()
        except UnlockError as ue:
            print "Could not unlock database"
            print str(ue)
            return "Committed, but could not unlock db"

        print "Closing device handle"
        self.dev.close()
        return "Completed with diff: " + diff


