import abc
from a_frame.utils.action_providers.action_base import ActionBase
import tempfile
import os
import subprocess


class ShellExecution(ActionBase):
    """
        Runs a template as a local script
        !!! Potentially dangerous !!!
        Essentially runs untrusted user input on the local box

        By convention use the execute_template will create a local script, set it chmod +x
        device details will be set in the ENV as
        ENDPOINT_IP
        ENDPOINT_USERNAME
        ENDPOINT_PASSWORD
    """

    endpoint_ip = ""
    endpoint_username = ""
    endpoint_password = ""

    def set_endpoint(self, endpoint):
        self.endpoint_ip = endpoint["ip"]
        self.endpoint_username = endpoint["username"]
        self.endpoint_password = endpoint["password"]
        return

    def execute_template(self, template):
        """
        writes the template to a tmp file and executes it on the server.
        Potentially very dangerous. You probably shouldn"t do this!

        If you do want to do this ( you shouldn"t ), your script should
        look for the device endpoint parameters stored in the env as
        ENDPOINT_USERNAME
        ENDPOINT_PASSWORD
        ENDPOINT_IP

        :param template: some sort of executable script
        :return: String results from the output of the script
        """

        cleaned_template = template.replace('\r\n', '\n')

        f = tempfile.NamedTemporaryFile()
        f.write(cleaned_template)
        f.flush()

        os.chmod(f.name, 0700)
        env = os.environ.copy()

        env["ENDPOINT_USERNAME"] = self.endpoint_username
        env["ENDPOINT_PASSWORD"] = self.endpoint_password
        env["ENDPOINT_IP"] = self.endpoint_ip

        print self.endpoint_ip

        output = subprocess.check_output(f.name, shell=True, env=env)
        print output
        f.close()
        return output


