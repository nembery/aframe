#
# screen_tags

# this custom tag library allows access to various utility functions.
# These are espescially useful in creating custom output_parsers for automations.

# If you need to do more than simple data manipulation using javascript in the template, then
# adding a tag here allows access to raw python
#
# useage:
# First, load the library in the output parser template with:
#
# {% load poll_extras %}
#
# then {% parse_json results as results_json %}
# {{ results_json }}
#
import json
import logging

from django import template
from screens.models import Screen, ScreenLabel

register = template.Library()
logger = logging.getLogger(__name__)


@register.simple_tag
def parse_json(input_string):
    """
    Takes a json encoded input string and returns the python object. Uses the json.loads function
    Returns an empty dict on error. The results should be set as a variable using the 'as' argument
    :param input_string: json encoded string
    :return: python object
    """
    try:
        return json.loads(input_string)
    except ValueError:
        logger.error('Could not parse json data in parse_json template tag!')
        return {}


@register.simple_tag
def get_label_value(screen_object, label_name, default='n/a'):
    """
    Takes a screen object and returns the value of the desired tag. Returns the first tag found if there are more
    than one associated with a screen
    :param screen_object: Screen
    :param label_name: Label with 'name' == name
    :param default: default value if no label was found
    :return: value of Label
    """
    label = screen_object.labels.filter(name=label_name).first()
    if label is None:
        return default

    return label.value


@register.simple_tag
def get_screens_with_label(label_name, label_value=''):
    """
    Returns a list of screens that match the exact label name and value. Useful for building menus or hierarchies
    :param label_name: name field of label to match
    :param label_value: value field of label to match, optional
    :return: list of Screens
    """
    if label_value == '':
        screens = Screen.objects.filter(labels__name=label_name).order_by('name').all()
    else:
        screens = Screen.objects.filter(labels__name=label_name, labels__value=label_value).order_by('name').all()
    return screens


@register.simple_tag
def get_screens_grouped_by_label(label_name, label_value=''):
    """
    Returns a dict of labels with a dict of values each with a list of screens that match the exact label name and
    value. Useful for building menus or hierarchies
    :param label_name: name field of label to match
    :param label_value: value field of label to match, optional
    :return: list of Screens
    """
    label_groups = dict()
    if label_value == '':
        screens = Screen.objects.filter(labels__name=label_name).order_by('name').all()
        for s in screens:
            label_value = s.labels.filter(name=label_name).first().value
            if label_value not in label_groups:
                label_groups[label_value] = list()

            label_groups[label_value].append(s)

    else:
        screens = Screen.objects.filter(labels__name=label_name, labels__value=label_value).order_by('name').all()
        label_groups[label_value] = screens

    return label_groups


@register.simple_tag
def get_label_values_for_name(label_name):
    """
    Return a list of all label values for the given label name
    :param label_name: Label with 'name' == name
    :return: list of values
    """
    return ScreenLabel.objects.filter(name=label_name).values_list('value')
