import os
import yaml

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
    print "checking path %s" % path
    path_array = path.split('.')
    element = str(path_array[0])
    if element in json_object:
        print "Found %s" % element
        # we have it!
        if len(path_array) == 1:
            print "returning last element %s " % element
            print "it is %s" % json_object[element]
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
                print "recursively searching %s" % new_path
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
                print "recursing %s" % new_path
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
            print "recursively searching %s" % new_path
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
                print "recursively searching %s" % new_path
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
            print "recursively searching %s" % str(v)
            depth += 1
            r = get_list_from_json(key, value, v, kv_list, depth)
            if r is not None:
                print "returning from list with success %s" % depth
                return r

        print "returning from list none %s" % depth
        return None

    elif type(data_structure) == dict:
        if key in data_structure and value in data_structure:
            print "FOUND IT"
            d = dict()
            d["key"] = data_structure[key]
            d["value"] = data_structure[value]
            print "returning %s" % depth
            kv_list.append(d)
            return kv_list
        else:
            for k in data_structure:
                v = data_structure[k]
                print "recursively searching %s" % str(v)
                depth += 1
                r = get_list_from_json(key, value, v, kv_list, depth)
                if r is not None:
                    print "returning from dict with success %s" % depth
                    return r

            print "returning from dict none %s" % depth
            return None

    print "finally: " + str(depth)
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
            # print "recursively searching %s" % str(v)
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
                # print "recursively searching %s" % str(v)
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
        secrets = yaml.load(secrets_file)

    return secrets


def get_secrets_keys():
    """
    used for UI select lists
    :return: a list of dicts that represent key/label pairs of entries in the secrets file.
    The form is [ {'name': 'some_key', 'label': 'Some Label' } ]
    """
    secret_keys = list()
    secrets = _load_secrets()
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
    return secrets['secrets'][key]['value']
