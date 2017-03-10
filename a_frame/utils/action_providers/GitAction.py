import base64
import json
import platform
import ssl
import urllib2
from urllib2 import HTTPError
from lxml import etree
from a_frame.utils.action_providers.action_base import ActionBase

import git
import os


class GitAction(ActionBase):
    """
        Simple Git action provider

        This is a "standalone" action, meaning it will be executed without an endpoint being passed in
    """
    
    remote_url = ''
    repository_name = 'git_action'
    local_directory = '/var/cache/aframe/'
    target_branch = 'master'
    target_directory = '/'
    target_filename = 'test'
    commit_message = 'Committed From Aframe'

    def execute_template(self, template):
        """
        We now have the global config (if any), the instance config, and the completed template from the input_form
        and can perform the desired request
        :param template: the completed template from the user or API
        :return Boolean based on execution outcome.
        """
        print "executing %s" % template

        local_directory = '/var/cache/aframe/' + self.repository_name

        if not os.path.exists(self.local_directory):
            os.makedirs(self.local_directory)

        try:
            repo = git.Repo(self.local_directory)

        except git.exc.InvalidGitRepositoryError:
            repo = git.Repo.init(self.local_directory, bare=False)

        if len(repo.remotes) == 0:
            # this shouldn't happen
            # but if we happen to get a local repo that's already been
            # defined but no remotes
            origin = repo.create_remote('origin', url=self.remote_url)
        else:
            origin = repo.remotes.origin

        try:
            origin.fetch()
        except git.exc.GitCommandError as gec:
            print gec
            return "Could not init remote git repo"

        try:
            # let's ensure we have the latest and greatest
            origin.pull()
            # in this case we don't actually need to set tracking or
            # to push configs back upstream
            if self.target_branch in origin.refs:
                repo.create_head(self.target_branch, origin.refs[self.target_branch])
                this_repo_head = repo.heads[self.target_branch]
                this_repo_head.set_tracking_branch(origin.refs[self.target_branch])
                this_repo_head.checkout()

            target_directory_path = self.local_directory + self.target_directory
            if not os.path.exists(target_directory_path):
                os.makedirs(target_directory_path)

            if not target_directory_path.endswith('/'):
                target_directory_path += '/'

            target_file_path = target_directory_path + self.target_filename

            with open(target_file_path, 'wb') as tfp:
                tfp.write(template)

            repo.git.add(A=True)
            repo.index.commit(self.commit_message)
            origin.push()

        except Exception as e:
            print str(e)
            return "Error committing to remote git repo"

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

