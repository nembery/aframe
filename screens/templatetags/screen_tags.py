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
