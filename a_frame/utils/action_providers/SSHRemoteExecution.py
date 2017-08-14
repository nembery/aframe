import uuid

import paramiko
from paramiko.ssh_exception import SSHException

from a_frame.utils.action_providers.action_base import ActionBase


class SSHRemoteExecution(ActionBase):
    """
        Runs a template as a remote script

        Will either run a CLI on a remote host via SSH
        or use SCP to place a compiled template on that host

        FIXME - maybe this should actually scp and execute all at once?
        device details will be set in the ENV as
        ENDPOINT_IP
        ENDPOINT_USERNAME
        ENDPOINT_PASSWORD
    """

    endpoint_ip = ""
    endpoint_username = ""
    endpoint_password = ""

    request_type = "cli"
    file_path = "/tmp/aframe/script.sh"

    def set_endpoint(self, endpoint):
        self.endpoint_ip = endpoint["ip"]
        self.endpoint_username = endpoint["username"]
        self.endpoint_password = endpoint["password"]
        return

    def execute_template(self, template):
        """
        switches based on request_type chosen from template configuration

        :param template:
        :return: String results from the endpoint netconf subsystem
        """

        # let's ensure we don't have silly dos style line breaks
        template = template.replace("\r\n", "\n")
        template = template.replace("\r", "\n")

        if self.request_type == "scp":
            return self.scp_template(template)
        elif self.request_type == "scp_and_execute":
            # first copy over the template
            self.scp_template(template)
            # this will update the file_path if necessary
            # so, now let's just call execute_cli on the file_path
            return self.execute_cli(self.file_path)
        else:
            return self.execute_cli(template)

    def execute_cli(self, template):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=self.endpoint_ip, username=self.endpoint_username, password=self.endpoint_password)
            stdin, stdout, stderr = client.exec_command(template)
            err = stderr.read()
            if err != "":
                return err
            else:
                return stdout.read()
        except SSHException as se:
            return str(se)

    def scp_template(self, template):
        """
        Uses scp to copy the template to the remote endpoint
        Hint, the file_path parameter can be overridden with the {{ syntax }}
        :param template:
        :return:
        """
        try:

            if self.file_path.endswith("/"):
                # bad news! no actual file name! let's use a random file name and continue
                new_path = self.file_path + str(uuid.uuid4())
                self.file_path = new_path

            # remove last thing after last "/"
            # results in only the path we care about
            script_path = "/".join(self.file_path.split('/')[:-1])
            transport = paramiko.Transport((self.endpoint_ip, 22))
            transport.connect(username=self.endpoint_username, password=self.endpoint_password)

            client = paramiko.SFTPClient.from_transport(transport)

        except SSHException as se:
            print "Caught SSHException"
            return str(se)

        try:
            print "Checking directory: " + script_path
            rstats = client.stat(script_path)
            print rstats
        except IOError:
            print "Creating non-existant path"
            client.mkdir(script_path)

        try:
            print "Writing file"
            f = client.file(self.file_path, 'w')
            f.write(template)
            f.close()
            print "setting execute permissions"
            client.chmod(self.file_path, 0744)
            client.close()

            log_message = "Wrote file %s with contents\n\n%s" % (self.file_path, template)
            return log_message

        except Exception as e:
            print "Caught error!"
            return str(e)
