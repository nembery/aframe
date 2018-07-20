import json
import logging
import os
import re
import socket
from urllib import quote
from urllib import unquote

import yaml
from django.template import engines
from django.template.base import VariableNode

from a_frame.utils import action_provider
from input_forms.models import InputForm
from screens.models import Screen
from screens.models import ScreenWidgetConfig

from tools.models import ConfigTemplate

logger = logging.getLogger(__name__)


def generate_dict(path, val):
    d = dict()
    path_array = path.split('.')
    first = path_array[0]
    if len(path_array) == 1:
        d[first] = val
        return d
    else:
        new_path = '.'.join(path_array[1:])
        d[first] = generate_dict(new_path, val)
        return d


def get_value_from_json(path, json_object):
    """
    Simple recursive function to search a json object for the path
    i.e. turn data.test.name into data["test"]["name"]
    :param path: path notation 'data.test.name'
    :param json_object: the json object to search
    :return: value of data["test"]["name"]
    """
    print("checking path %s" % path)
    path_array = path.split('.')
    element = str(path_array[0])
    if element in json_object:
        print("Found %s" % element)
        # we have it!
        if len(path_array) == 1:
            print("returning last element %s " % element)
            print("it is %s" % json_object[element])
            return json_object[element]
        else:
            new_json_object = json_object[element]
            new_path_array = path_array[1:]
            new_path = '.'.join(new_path_array)
            return get_value_from_json(new_path, new_json_object)
    else:
        return "NOT FOUND"


def get_path_for_value_from_json(data_structure, target, path):
    """
    Given a JSON data structure,  find the json path notation to a given value
    :param data_structure: json object
    :param target: key we are looking for
    :param path: current path to said key
    :return: JSON path notation to the given key
    """
    if type(data_structure) == list:
        for v in data_structure:
            if type(v) == str and v == target:
                return "%s[%s]" % (path, data_structure.index(v))
            elif type(v) == unicode and str(v) == target:
                return "%s[%s]" % (path, data_structure.index(v))
            else:
                new_path = "%s[%s]" % (path, data_structure.index(v))
                print("recursively searching %s" % new_path)
                r = get_path_for_value_from_json(v, target, new_path)
                if r is not None:
                    return r

    elif type(data_structure) == dict:
        for k in data_structure:
            v = data_structure[k]
            if type(v) == str and v == target:
                return "%s[%s]" % (path, k)
            elif type(v) == unicode and str(v) == target:
                return "%s[\"%s\"]" % (path, k)
            else:
                new_path = "%s[\"%s\"]" % (path, k)
                print("recursing %s" % new_path)
                r = get_path_for_value_from_json(v, target, new_path)
                if r is not None:
                    return r

    elif type(data_structure) == unicode:
        if str(data_structure) == target:
            return path

    elif type(data_structure) == str:
        if data_structure == target:
            return path

    else:
        if str(data_structure) == target:
            return path


def get_path_for_key_from_json(data_structure, target, path):
    """
    Given a JSON data structure,  find the json path notation to a given key
    :param data_structure: json object
    :param target: key we are looking for
    :param path: current path to said key
    :return: JSON path notation to the given key
    """
    if type(data_structure) == list:
        for v in data_structure:
            new_path = "%s[%s]" % (path, data_structure.index(v))
            print("recursively searching %s" % new_path)
            r = get_path_for_key_from_json(v, target, new_path)
            if r is not None:
                return r

    elif type(data_structure) == dict:
        for k in data_structure:
            v = data_structure[k]
            if type(k) == str and k == target:
                return "%s[%s]" % (path, k)
            elif type(k) == unicode and str(k) == target:
                return "%s[\"%s\"]" % (path, k)
            else:
                new_path = "%s[\"%s\"]" % (path, k)
                print("recursively searching %s" % new_path)
                r = get_path_for_key_from_json(v, target, new_path)
                if r is not None:
                    return r

    elif type(data_structure) == unicode:
        if str(data_structure) == target:
            return path

    elif type(data_structure) == str:
        if data_structure == target:
            return path

    else:
        if str(data_structure) == target:
            return path


def get_list_from_json(key, value, data_structure, kv_list=[], depth=0):
    """
    Given a data_structure look for dicts with keys that match key and value. Return a list of tuples of the values
    of those dicts. Will search to arbitrary depth.
    example:
        data_structure: [ { "id": 1, "name": "name1" }, { "id": 2, "name": "name2"} ]
        key: "id"
        value: "name"
        return [(1, "name1"), (2, "name2")]

    :param key: key of a dict of which to return as the 'key' of our new list
    :param value: key of a dict of which to return as the 'value' of our new dict
    :param data_structure: python data_structure
    :param kv_list: list to be returned
    :return: list of tuples
    """

    if type(data_structure) == list:
        for v in data_structure:
            print("recursively searching %s" % str(v))
            depth += 1
            r = get_list_from_json(key, value, v, kv_list, depth)
            if r is None:
                return r
        print("returning from list none %s" % depth)
        return kv_list

    elif type(data_structure) == dict:
        if key in data_structure and value in data_structure:
            d = dict()
            d["key"] = data_structure[key]
            d["value"] = data_structure[value]
            print("returning %s" % depth)
            kv_list.append(d)
            return kv_list
        else:
            for k in data_structure:
                v = data_structure[k]
                print("recursively searching %s" % str(v))
                depth += 1
                r = get_list_from_json(key, value, v, kv_list, depth)
                if r is not None:
                    print("returning from dict with success %s" % depth)
                    return r

            print("returning from dict none %s" % depth)
            return None

    print("finally: " + str(depth))
    if depth == 0:
        return kv_list
    else:
        return None


def get_value_for_key_from_json(key, data_structure):
    """
    Given a data_structure return the *first* value of the key from the first dict
    example:
        data_structure: [ { "id": 1, "name": "name1" }, { "id": 2, "name": "name2"} ]
        key: "id"
        return 1

    :param key: key of a dict of which to return the value
    :param data_structure: python data_structure
    :return: value of key in first dict found
    """

    if type(data_structure) == list:
        for v in data_structure:
            # print("recursively searching %s" % str(v))
            r = get_value_for_key_from_json(key, v)
            if r is not None:
                return r

        return None

    elif type(data_structure) == dict:
        if key in data_structure:
            return data_structure[key]
        else:
            for k in data_structure:
                v = data_structure[k]
                # print("recursively searching %s" % str(v))
                r = get_value_for_key_from_json(key, v)
                if r is not None:
                    return r

    return None


def _load_secrets():
    """
    find the secrets.yml file in the 'conf' directory and return the yaml parsed value
    :return: secrets object in the form {'secrets': {'key': {'label': 'some label', 'value': 'some_password' } } }
    """
    common_lib_dir = os.path.dirname(os.path.abspath(__file__))
    conf_dir = os.path.abspath(os.path.join(common_lib_dir, '../../conf'))
    secrets_file_path = os.path.join(conf_dir, 'secrets.yml')
    with open(secrets_file_path, 'r') as secrets_file:
        try:
            secrets = yaml.load(secrets_file)
        except yaml.scanner.ScannerError as se:
            logger.error('Could not parse secrets file!')
            logger.error(se)
            secrets = {'secrets': {'default': {'label': 'default', 'value': 'password123'}}}

    return secrets


def get_secrets_keys():
    """
    used for UI select lists
    :return: a list of dicts that represent key/label pairs of entries in the secrets file.
    The form is [ {'name': 'some_key', 'label': 'Some Label' } ]
    """
    secret_keys = list()
    secrets = _load_secrets()
    if 'secrets' in secrets:
        for key in secrets['secrets']:
            item = dict()
            item['name'] = key
            item['label'] = secrets['secrets'][key]['label']
            secret_keys.append(item)

    return secret_keys


def lookup_secret(key):
    """
    load the secrets file and return the value by key
    :param key: key to use for lookup
    :return: string value of the secret
    """
    secrets = _load_secrets()
    if 'secrets' in secrets:
        if key in secrets['secrets']:
            return secrets['secrets'][key]['value']
        else:
            logger.warn('desired secret key was not found!')

    return 'password123'


def execute_template(post_vars):
    """
    Refactored out of tools/views.py as this is used in a couple of different places (tools/views and screens/views)
    :param post_vars: copy of all variables passed in via the operation
    :return: response object of form {'output': whatever, 'status': 1 }
    """
    if 'template_id' not in post_vars and 'template_name' not in post_vars:
        error = {'output': 'missing required template_id or template_name parameter', 'status': 1}
        return error

    if 'template_id' in post_vars:
        template_id = int(post_vars['template_id'])
        config_template = ConfigTemplate.objects.get(pk=template_id)
    else:
        template_name = str(post_vars['template_name'])
        print("GETTING %s" % template_name)
        config_template = ConfigTemplate.objects.get(name=template_name)

    template_api = get_input_parameters_for_template(config_template)

    context = dict()

    try:
        print(str(template_api["input_parameters"]))
        input_parameters = template_api["input_parameters"]

        for j in input_parameters:
            print("setting context %s" % j)
            context[j] = str(post_vars[j])

    except Exception as ex:
        print(str(ex))
        error = {"output": "missing required parameters", "status": 1}
        return error

    compiled_template = engines['django'].from_string(config_template.template)
    # compiled_template = get_template_from_string(config_template.template)
    completed_template = str(compiled_template.render(context))

    print(completed_template)
    action_name = config_template.action_provider
    action_options = json.loads(config_template.action_provider_options)

    print(post_vars)

    for ao in action_options:
        print('checking ' + str(ao))
        if "action_options_" + str(ao) in post_vars:
            print("found a match!")
            new_val = post_vars["action_options_" + str(ao)]
            print(new_val)
            current_value = action_options[ao]["value"]
            print(current_value)
            action_options[ao]["value"] = re.sub("{{ .* }}", new_val, current_value)
            print(action_options[ao]["value"])

    # let's load any secrets if necessary
    provider_options = action_provider.get_options_for_provider(action_name)
    for opt in provider_options:
        if opt['type'] == 'secret':
            opt_name = opt['name']
            pw_lookup_key = action_options[opt_name]['value']
            pw_lookup_value = lookup_secret(pw_lookup_key)
            action_options[opt_name]['value'] = pw_lookup_value

    print("action name is: " + action_name)

    action = action_provider.get_provider_instance(action_name, action_options)
    if config_template.type == "per-endpoint":

        if "af_endpoint_ip" not in post_vars or "af_endpoint_id" not in post_vars:
            error = {"output": "missing required authentication parameters", "status": 1}
            return error

        endpoint = dict()
        endpoint["id"] = post_vars.get("af_endpoint_id", "")
        endpoint["name"] = post_vars.get("af_endpoint_name", "")
        endpoint["ip"] = post_vars.get("af_endpoint_ip", "")
        endpoint["username"] = post_vars.get("af_endpoint_username", "")
        endpoint["password"] = post_vars.get("af_endpoint_password", "")
        endpoint["type"] = post_vars.get("af_endpoint_type", "")

        action.set_endpoint(endpoint)

    try:
        results = action.execute_template(completed_template.strip().replace('\r\n', '\n'))
        response = {"output": results.strip(), "status": 0}

    except Exception as ex:
        print(str(ex))
        response = {"output": "Error executing template", "status": 1}

    return response


def get_input_parameters_for_template(config_template):
    t = engines['django'].from_string(config_template.template)
    # t = get_template_from_string(config_template.template)
    input_parameters = []
    for node in t.template.nodelist:
        defined_tags = node.get_nodes_by_type(VariableNode)
        for v in defined_tags:
            print("adding %s as an available tag" % v.filter_expression)
            variable_string = str(v.filter_expression)
            if variable_string not in input_parameters:
                if not variable_string.startswith("af_"):
                    # skip internal af parameters
                    input_parameters.append(variable_string)

    # FIXME maybe move these to the settings.py ?
    host = socket.gethostname()
    url = "/tools/execute_template"

    action_options = json.loads(config_template.action_provider_options)
    action_option_variables = list()

    for action_option in action_options:
        opts = action_options[action_option]
        if "variable" in opts and opts["variable"] != '':
            print(action_option)
            item = dict()
            item['name'] = 'action_options_' + opts['name']
            item['default'] = opts['variable']
            action_option_variables.append(item)

    template_usage = {
        "id": config_template.id,
        "name": config_template.name,
        "description": config_template.description,
        "a_frame_url": "http://" + host + url,
        "input_parameters": input_parameters,
        "action_option_variables": action_option_variables
    }

    print(config_template.type)

    if config_template.type == "per-endpoint":
        input_parameters.append("af_endpoint_ip")
        input_parameters.append("af_endpoint_username")
        input_parameters.append("af_endpoint_password")
        input_parameters.append("af_endpoint_type")

    return template_usage


def export_input_form(input_form_id):
    input_form = InputForm.objects.get(pk=input_form_id)
    config_template = input_form.script

    template_options = dict()
    template_options["name"] = config_template.name
    template_options["description"] = config_template.description
    template_options["action_provider"] = config_template.action_provider
    template_options["action_provider_options"] = config_template.action_provider_options
    template_options["type"] = config_template.type
    template_options["template"] = quote(config_template.template)

    form_options = dict()
    form_options["name"] = input_form.name
    form_options["description"] = input_form.description
    form_options["instructions"] = input_form.instructions
    form_options["json"] = quote(input_form.json)

    exported_object = dict()
    exported_object["template"] = template_options
    exported_object["form"] = form_options
    input_form_json = json.dumps(exported_object)
    logger.debug(input_form_json)
    return input_form_json


def get_screen_themes():
    """
    Return a list of all theme files in the screens/templates/themes directory
    :return: list of filenames ending with html
    """
    common_lib_dir = os.path.dirname(os.path.abspath(__file__))
    themes_dir = os.path.abspath(os.path.join(common_lib_dir, '../../screens/templates/themes'))
    themes = list()
    for t in os.listdir(themes_dir):
        if t.endswith('.html'):
            th = dict()
            th['label'] = t.replace('.html', '')
            th['base_template'] = 'themes/%s' % t
            themes.append(th)

    print('RETURNING THEMES')
    print(themes)
    return themes


def import_form(jd):
    """
    Imports an input_from from serialized json data
    :param jd: json_data object generated from the export_input_form function
    :return: id of the input form or id of the input form if it already exists
    """
    template_options = jd["template"]
    form_options = jd["form"]

    if not ConfigTemplate.objects.filter(name=template_options['name']).exists():
        template = ConfigTemplate()
        template.name = template_options["name"]
        template.description = template_options["description"]
        template.action_provider = template_options["action_provider"]
        template.action_provider_options = template_options["action_provider_options"]
        template.type = template_options["type"]
        template.template = unquote(template_options["template"])
        logger.info("Imported template: %s" % template.name)
        template.save()
    else:
        print('ConfigTemplate %s already exists' % template_options['name'])

    if not InputForm.objects.filter(name=form_options['name']).exists():
        input_form = InputForm()
        input_form.name = form_options["name"]
        input_form.description = form_options["description"]
        input_form.instructions = form_options["instructions"]
        input_form.json = unquote(form_options["json"])
        input_form.script = template

        logger.info("Import input form: %s" % input_form.name)
        input_form.save()
    else:
        print('Input form %s already exists' % form_options['name'])
        input_form = InputForm.objects.get(name=form_options['name'])

    return input_form.id


def load_config():
    common_lib_dir = os.path.dirname(os.path.abspath(__file__))
    conf_dir = os.path.abspath(os.path.join(common_lib_dir, '../../conf'))
    conf_file_path = os.path.join(conf_dir, 'aframe.conf')
    with open(conf_file_path, 'r') as conf_file:
        try:
            conf = yaml.load(conf_file)
        except yaml.scanner.ScannerError as se:
            logger.error('Could not parse conf file!')
            logger.error(se)
            conf = {'default_screen': ''}

    return conf


def import_screen(json_data):
    try:
        # screen export creates a dict with two keys 'screen' and 'input_forms'
        # 'screen' key holds metadata about the screen
        screen_data = json_data['screen']

        if Screen.objects.filter(name=screen_data['name'], description=screen_data['description']) \
                .exists():
            logger.info('Skipping existing screen %s' % screen_data['name'])
            return None

        # 'input_forms' holds all the referenced input_forms in that screen
        # each of these is 'exported' in whole, serialized, and kept here
        form_data = json_data['input_forms']

        # we will also export any global widget data that is found on widgets in the screen
        if 'widgets' not in json_data:
            widget_data = dict()
        else:
            widget_data = json_data['widgets']

        for w in widget_data:
            if not ScreenWidgetConfig.objects.filter(widget_type=w).exists():
                widget_config = ScreenWidgetConfig()

                widget_config.widget_type = w
                widget_config.data = unquote(widget_data[w])
                widget_config.save()

        # we need to update the layout with new input form ids after we import those
        layout = json.loads(screen_data['layout'])

        # create new layout object
        new_layout = dict()
        if 'widgets' not in layout:
            layout['widgets'] = dict()

        # we can just copy the widgets right in
        new_layout['widgets'] = layout['widgets']
        new_layout['input_forms'] = dict()

        # iterate over all exported input forms
        for sid in form_data.keys():
            # let's get the entire form that was previously exported in full
            screen_form = form_data[sid]
            # convert back from json
            screen_form_data = json.loads(screen_form)
            # do the import here and get it's updated ID
            new_id = import_form(screen_form_data)
            # these should absolutely already exist in the layout
            if sid in layout['input_forms'].keys():
                logger.info('updating layout %s to %s' % (sid, new_id))
                new_layout['input_forms'][new_id] = layout['input_forms'][sid]

        if 'tag' not in screen_data:
            screen_data['tag'] = 'aframe'

        screen = Screen()
        screen.name = screen_data['name']
        screen.description = screen_data['description']
        screen.theme = screen_data['theme']
        screen.id = screen_data['id']
        screen.tag = screen_data['tag']
        screen.layout = json.dumps(new_layout)
        screen.save()

    except KeyError as ke:
        logger.info('some keyerror')
        logger.info(ke)
        logger.error('Could not import screen!')
        return None
