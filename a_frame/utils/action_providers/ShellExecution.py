import os
import subprocess
import time
import uuid
from subprocess import CalledProcessError

from a_frame.utils.action_providers.action_base import ActionBase


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
        path = "/tmp/" + str(uuid.uuid4())
        f = open(path, "w+")
        f.write(cleaned_template)
        f.flush()
        time.sleep(.5)
        filename = f.name
        os.chmod(filename, 0700)
        f.close()
        env = os.environ.copy()

        env["ENDPOINT_USERNAME"] = self.endpoint_username
        env["ENDPOINT_PASSWORD"] = self.endpoint_password
        env["ENDPOINT_IP"] = self.endpoint_ip

        print self.endpoint_ip

        try:
            output = subprocess.check_output(filename, shell=True, env=env)
            print output
            return output
        except CalledProcessError as cpe:
            o = "Error calling local script"
            o += subprocess.check_output('cat %s' % filename, shell=True, env=env)
            o += "\n-----------------------------\n"
            o += str(cpe)
            o += "\n-----------------------------\n"
            print o
            return o
