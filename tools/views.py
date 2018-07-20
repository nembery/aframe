from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template.base import VariableNode
from django.core.cache import cache

# from django.template.loader import get_template_from_string
from django.template import engines

import logging
import json
import re
import socket

from tools.models import ConfigTemplate
from input_forms.models import InputForm
from a_frame.utils import action_provider
from a_frame import settings
from common.lib import aframe_utils

logger = logging.getLogger(__name__)


def index(request):
    template_list = ConfigTemplate.objects.all().order_by("name")
    context = {"template_list": template_list}
    return render(request, "configTemplates/index.html", context)


def choose_action(request):
    action_providers = action_provider.get_action_provider_select()

    context = {"action_providers": action_providers}
    return render(request, "configTemplates/choose_action.html", context)


def configure_action(request):
    """
    FIXME - add some validation here
    :param request:
    :return:
    """
    required_fields = set(["action_provider"])
    if not required_fields.issubset(request.POST):
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    provider_name = request.POST["action_provider"]

    action_options = action_provider.get_options_for_provider(provider_name)
    secrets = aframe_utils.get_secrets_keys()

    if action_options == "":
        context = {"error": "action provider not found"}
        return render(request, "error.html", context)

    context = {"action_options": action_options, "action_provider": provider_name, "secrets": secrets}
    return render(request, "configTemplates/configure_action.html", context)


def define_template(request):
    action_provider_name = request.POST["action_provider"]
    options = action_provider.get_options_for_provider(action_provider_name)
    configured_options = dict()
    for opt in options:

        if "name" in opt and opt["name"] in request.POST:
            o = dict()
            o["name"] = opt["name"]
            o["value"] = request.POST[opt["name"]]
            o["label"] = opt["label"]

            # check for hidden action option customization
            if opt["name"] + "_variable" in request.POST:
                o["variable"] = request.POST[opt["name"] + "_variable"]

            configured_options[o["name"]] = o
        else:
            context = {"error": "Required option not found in request!"}
            return render(request, "error.html", context)

    print("Setting configured options to the session %s" % configured_options)
    request.session["new_template_action_options"] = configured_options
    context = {"options": configured_options, "action_provider": action_provider_name}
    return render(request, "configTemplates/define_template.html", context)


def get_options_for_action(request):
    action_name = request.POST["action_name"]
    print(action_name)
    for a in settings.ACTION_PROVIDERS:
        print(a)
        if a["name"] == action_name:
            return HttpResponse(json.dumps(a), content_type="application/json")


def edit(request, template_id):
    template = get_object_or_404(ConfigTemplate, pk=template_id)

    default_options = action_provider.get_options_for_provider(template.action_provider)
    action_options = json.loads(template.action_provider_options)
    secrets = aframe_utils.get_secrets_keys()

    context = {"template": template,
               "action_options": json.dumps(action_options),
               "default_options": default_options,
               "secrets": secrets
               }
    return render(request, "configTemplates/edit.html", context)


def update(request):
    try:
        if "id" in request.POST:
            template_id = request.POST["id"]
            template = get_object_or_404(ConfigTemplate, pk=template_id)
            template.name = request.POST["name"]
            template.description = request.POST["description"]
            template.template = request.POST["template"]
            template.type = request.POST["type"]

            options = action_provider.get_options_for_provider(template.action_provider)
            configured_options = dict()
            for opt in options:
                print("Checking %s" % opt["name"])
                if opt["name"] in request.POST:
                    o = dict()
                    o["name"] = opt["name"]
                    o["value"] = request.POST[opt["name"]]
                    o["label"] = opt["label"]

                    # check for hidden action option customization
                    if opt["name"] + "_variable" in request.POST:
                        print("FOUND VARIABLE in tools update!")
                        print("value is %s " % request.POST[opt["name"] + "_variable"])
                        o["variable"] = request.POST[opt["name"] + "_variable"]

                    configured_options[o["name"]] = o
                else:
                    context = {"error": "Required option not found in request!"}
                    return render(request, "error.html", context)

            template.action_provider_options = json.dumps(configured_options)
            template.save()
            try:
                input_form = InputForm.objects.get(script=template)
                return HttpResponseRedirect('/input_forms/edit/%s' % input_form.id)
            except InputForm.DoesNotExist as dne:
                return HttpResponseRedirect("/input_forms/view_from_template/%s" % template.id)

        else:
            return render(request, "error.html", {
                "error": "Invalid data in POST"
            })

    except KeyError:
        return render(request, "error.html", {
            "error": "Invalid data in POST - Key error"
        })


def create(request):
    required_fields = set(["name", "description", "template", "type"])
    if not required_fields.issubset(request.POST):
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    template = ConfigTemplate()
    template.name = request.POST["name"]
    template.description = request.POST["description"]
    template.action_provider = request.POST["action_provider"]
    template.template = request.POST["template"].strip().replace('\r\n', '\n')
    template.type = request.POST["type"]

    if "new_template_action_options" not in request.session:
        return render(request, "error.html", {
            "error": "Invalid session data!"
        })

    configured_action_options = request.session["new_template_action_options"]
    template.action_provider_options = json.dumps(configured_action_options)
    print("action options are:")
    print(configured_action_options)
    print("Saving form")
    template.save()
    return HttpResponseRedirect("/input_forms/view_from_template/%s" % template.id)


def clone(request, template_id):
    """
    Clones a template. Allows quickly creating new templates from existing ones.

    :param request:
    :param template_id: id of the template to be cloned
    :return: redirect to edit screen of new template!
    """
    template = get_object_or_404(ConfigTemplate, pk=template_id)

    # create our Dolly the sheep (clone)
    dolly = ConfigTemplate()
    dolly.name = template.name + " Clone"
    dolly.description = template.description
    dolly.action_provider = template.action_provider
    dolly.action_provider_options = template.action_provider_options
    dolly.template = template.template
    dolly.type = template.type

    print("Cloning template %s" % template.name)
    dolly.save()
    dollies_id = dolly.id

    # attempt to save any existing input form associations on the session
    # we'll retrieve this later when creating a new input form
    try:
        input_form = InputForm.objects.get(script=template)

        if 'cloned_templates' in request.session:
            cloned_templates = request.session['cloned_templates']
        else:
            cloned_templates = dict()

        cloned_templates[dollies_id] = dict()
        cloned_templates[dollies_id]['cloned_from'] = template.id
        cloned_templates[dollies_id]['input_form_id'] = input_form.id
        print('added a template to the cloned templates cache in the session')
        print(dollies_id)

        request.session['cloned_templates'] = cloned_templates

    except InputForm.DoesNotExist as dne:
        print('Could not find input_form for this cloned template')

    return HttpResponseRedirect('/tools/edit/%s/' % dolly.id)


def detail(request, template_id):
    template = get_object_or_404(ConfigTemplate, pk=template_id)
    return render(request, "configTemplates/details.html", {"template": template})


def delete(request, template_id):
    template = get_object_or_404(ConfigTemplate, pk=template_id)
    template.delete()
    return HttpResponseRedirect("/input_forms/")


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
            # item['name'] = 'action_options_' + opts['name']
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


def get_template_input_parameters_overlay(request):
    """
    Describes how to embed the given template
    :param request:
    :return: json payload describing how to embed this template
    """

    required_fields = set(["template_name"])
    if not required_fields.issubset(request.POST):
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    template_name = request.POST["template_name"]

    config_template = get_object_or_404(ConfigTemplate, name=template_name)
    template_usage = get_input_parameters_for_template(config_template)
    template_usage['a_frame_url'] = '{}://{}/tools/execute_template'.format(request.scheme, request.get_host())

    return render(request, "configTemplates/overlay.html", template_usage)


def execute_template(request):
    """
    Executes an automation template, you must supply at least a template_id or template_name
    If the automation template requires input parameters or action options, those must also be supplied as well

    :param request: HTTPRequest
    :return: json object of the form:
        {"output": "output of the automation template", "status": "0 or 1 for success or failure"
    """
    post_vars = request.POST.dict()

    response = aframe_utils.execute_template(post_vars)
    return HttpResponse(json.dumps(response), content_type="application/json")


def search(request):
    """
    used for UI autocomplete searches. Only used on the endpoint details page. Filter out standalone type templates
    :param request:
    :return:
    """
    term = request.GET["term"]
    template_list = ConfigTemplate.objects.filter(name__contains=term)
    results = []
    for template in template_list:
        results.append(template.name)

    return HttpResponse(json.dumps(results), content_type="application/json")


def test_api(request):
    """
    Simple method for API usage example
    :param request: HttpRequest object either application/json encoded or x-www-form-urlencoded
    :return: json encoded string with data and status members
    """
    if request.META["CONTENT_TYPE"] == "application/json":
        try:
            data = json.loads(request.body)
        except ValueError:
            data = "Could not parse json message body!"

    elif request.META["CONTENT_TYPE"] == "application/x-www-form-urlencoded":
        if "data" in request.POST:
            data = request.POST["data"]
        else:
            data = "Unknown form data"

    else:
        data = "Unsupported content_type %s" % request.META["CONTENT_TYPE"]

    output = {"data": data, "status": "0"}
    return HttpResponse(json.dumps(output), content_type="application/json")


def chain_template(request):
    """
    Populates the input_variables of one template from POSTed form data or json encoded http request body
    This allows you to chain the output of one template to another one
    if the input_variable of a template is in the form 'some.variable.with.periods'
    then the input json object will be searched for that value
    :param request: HTTPRequest either x-www-form-urlencoded or application/json
    :return: the output of the template specified by the template_id parameter
    """
    print(request.META["CONTENT_TYPE"])
    if request.META["CONTENT_TYPE"] == "application/json":
        try:
            data = json.loads(request.body)
            template_id = data["template_id"]
        except ValueError:
            error = {"output": "missing required template_id parameter", "status": 1}
            return HttpResponse(json.dumps(error), content_type="application/json")

        try:
            config_template = ConfigTemplate.objects.get(pk=template_id)

            context = dict()
            # iterate over all the keys in the json object and set on the context
            # the template engine is smart enough to figure out what goes where
            for k in data:
                context[k] = data[k]

        except ObjectDoesNotExist:
            error = {"output": "Could not get config template", "status": 1}
            return HttpResponse(json.dumps(error), content_type="application/json")

    else:
        # this must be a x-www-form-urlencoded request
        required_fields = set(["template_id"])
        if not required_fields.issubset(request.POST):
            error = {"output": "missing required template_id parameter", "status": 1}
            return HttpResponse(json.dumps(error), content_type="application/json")

        template_id = request.POST["template_id"]
        config_template = ConfigTemplate.objects.get(pk=template_id)
        template_api = get_input_parameters_for_template(config_template)
        template_api['a_frame_url'] = '{}://{}/tools/execute_template'.format(request.scheme, request.get_host())
        context = dict()

        try:
            print(str(template_api["input_parameters"]))
            input_parameters = template_api["input_parameters"]

            for j in input_parameters:
                print("setting context %s" % j)
                context[j] = str(request.POST[j])

        except Exception as ex:
            print(str(ex))
            error = {"output": "missing required parameters", "status": 1}
            return HttpResponse(json.dumps(error), content_type="application/json")

    compiled_template = engines['django'].from_string(config_template.template)
    # compiled_template = get_template_from_string(config_template.template)
    completed_template = str(compiled_template.render(context))

    print(completed_template)
    action_name = config_template.action_provider
    action_options = json.loads(config_template.action_provider_options)

    print("action name is: " + action_name)

    action = action_provider.get_provider_instance(action_name, action_options)
    if config_template.type == "per-endpoint":
        required_fields = ("af_endpoint_ip", "af_endpoint_username",
                           "af_endpoint_password", "af_endpoint_password")

        if not required_fields.issubset(request.POST):
            error = {"output": "missing required authentication parameters", "status": 1}
            return HttpResponse(json.dumps(error), content_type="application/json")

        endpoint = dict()
        endpoint["ip"] = request.POST["af_endpoint_ip"]
        endpoint["username"] = request.POST["af_endpoint_username"]
        endpoint["password"] = request.POST["af_endpoint_password"]
        endpoint["type"] = request.POST["af_endpoint_type"]

        action.set_endpoint(endpoint)

    try:
        results = action.execute_template(completed_template.strip().replace('\r\n', '\n'))
        response = {"output": results, "status": 0}

    except Exception as ex:
        print(str(ex))
        response = {"output": "Error executing template", "status": 1}

    return HttpResponse(json.dumps(response), content_type="application/json")


def bind_automation(request):
    return render(request, "configTemplates/bind_automation.html")


def download_from_cache(request, cache_key):
    print('downloading cache object: %s' % cache_key)
    cache_object = cache.get(cache_key)
    filename = 'aframe_archive'
    if type(cache_object) is dict:
        if 'filename' in cache_object:
            print('Found a filename to use')
            filename = cache_object['filename']
            print(filename)

        response = HttpResponse(content_type=cache_object['content_type'])
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        response.write(cache_object['contents'])
        return response
    else:
        response = HttpResponse(content_type='application/x-binary')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        response.write(cache_object)
        return response


