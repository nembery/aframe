

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
