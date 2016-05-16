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
    result_msg = ""

    def set_endpoint(self, endpoint):
        try:
            # create the required iterator from the endpoint_list
            self.dev = Device(user=endpoint["username"], password=endpoint["password"], host=endpoint["ip"])
            self.dev.open(gather_facts=False)

        except Exception as err:
            print "Could not open device!"
            self.result_msg = str(err)
            self.dev = None

        return

    def execute_template(self, template):
        """
        switches based on request_type chosen from template configuration

        :param template:
        :return: String results from the endpoint netconf subsystem
        """
        if self.dev is None:
            return self.result_msg

        if self.request_type == "apply_template":
            return self.apply_template(template)
        elif self.request_type == "execute_cheat_command":
            return self.execute_cheat_command(template)
        elif self.request_type == "assert_set_configuration":
            return self.assert_set_configuration(template)
        elif self.request_type == "assert_xpath_configuration":
            return self.assert_xpath_configuration(template)
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

    def assert_set_configuration(self, pattern):

        print "Checking set command regex"
        config = self.dev.cli('show configuration | display set')
        print config
        config_pattern = re.compile(pattern)

        results = ""
        for line in config.split('\n'):
            if config_pattern.match(line):
                results += line + "\n"

        if results != "":
            return results

    def assert_xpath_configuration(self, xpath):

        print "Searching xpath"
        configuration_xml = self.dev.execute("<get-configuration></get-configuration>")
        print configuration_xml
        if configuration_xml.find(xpath):
            return "Configuration element: %s is present" % xpath

        return "not found"

    def apply_template(self, template):
        print self.dev
        conf_string = template.strip()
        # try to determine the format of our config_string
        config_format = "set"
        if re.search(r"^\s*<.*>$", conf_string, re.MULTILINE):
            config_format = "xml"
        elif re.search(r"^\s*(set|delete|replace|rename)\s", conf_string):
            config_format = "set"
        elif re.search(r"^[a-z:]*\s*\w+\s+{", conf_string, re.I) and re.search(r".*}\s*$", conf_string):
            config_format = "text"

        print "using format: " + config_format
        cu = Config(self.dev)
        try:
            cu.lock()
        except LockError as le:
            print "Could not lock database!"
            print str(le)
            self.dev.close()
            return "Failed to lock configuration database! %s" % str(le)

        try:
            print "loading config"
            cu.load(conf_string, format=config_format)
        except Exception as e:
            print "Could not load configuration"
            print str(e)
            try:
                cu.unlock()
            except UnlockError as ue:
                print str(ue)

            self.dev.close()
            return "Failed, could not load the configuration template. %s" % str(e)

        diff = cu.diff()
        print diff
        if diff is not None:
            try:
                cu.commit_check()
                print "Committing config!"
                cu.commit(comment="Commit via a_frame")

            except CommitError as ce:
                print "Could not load config! %s" % str(ce)
                cu.rollback()
                try:
                    print "Unlocking database!"
                    cu.unlock()
                except UnlockError as ue:
                    print "Could not unlock database"
                    print str(ue)
                print repr(ce)
                self.dev.close()
                return "Failed, commit check failed. %s" % str(ce)

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
            self.dev.close()
            return "Committed, but could not unlock db"

        print "Closing device handle"
        self.dev.close()
        return "Completed with diff: " + diff


