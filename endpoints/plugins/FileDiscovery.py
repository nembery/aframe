import abc
from endpoint_base import EndpointBase


class FileDiscovery(EndpointBase):
    """
        simplest of all endpoint list providers,
        load(data) will load a file from the given filename
        get_next() will iterate over the file omitting comments

        format expected is:
        id,name,ip,username,password,type
    """
    file_name = ""

    def get_config_options(self):
        """
        :return: List of configuration options for per-instance configuration
        """
        config = [
            {
                "name": "file_path",
                "label": "File Path",
                "type": "text",
                "value": "/var/tmp/some_file_name.txt"
            }
        ]
        return config

    def load_instance_config(self, config):
        filename = config["file_path"]["value"]
        try:
            self.file_name = open(filename)
        except IOError:
            print "Could not open filename!"
            self.file_name = iter(["0,Could not open file: %s!,error,error,error,error" % filename])
        return

    def get_next(self):
        print "get_next called"
        next_line = self.file_name.next()
        print next_line
        # ignore comments
        if not next_line.startswith("#"):
            print "found valid data"
            # remove line-breaks
            cleaned_line = next_line.replace("\n", "")
            # split on the comma
            endpoint_array = cleaned_line.split(",")
            # remove all quotes
            endpoint_array = map(lambda x: x.replace("\"", ""), endpoint_array)
            if len(endpoint_array) == 6:
                # use the splat operator to unpack the resulting line array
                # create_endpoint is a convenience function in the base class
                # feel free to modify this if your file format differs
                # expected argument ordering:
                # create_endpoint(endpoint_id, endpoint_name, ip, username, password, endpoint_type)
                endpoint = self.create_endpoint(*endpoint_array)
                print "returning endpoint"
                return endpoint
            else:
                print "Skipping malformed line - must have 6 parts"
                return self.get_next()
        else:
            # just continue in case of comments
            print "skipping comment"
            return self.get_next()
