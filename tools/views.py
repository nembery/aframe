from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.template.base import VariableNode
from django.template.loader import get_template_from_string
import json

from tools.models import ConfigTemplate
from tools.models import ConfigTemplateForm
from a_frame.utils import action_provider
from a_frame import settings


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
    provider_name = request.POST["action_provider"]

    action_options = action_provider.get_options_for_provider(provider_name)

    if action_options == "":
        context = {"error": "action provider not found"}
        return render(request, "error.html", context)

    context = {"action_options": action_options, "action_provider": provider_name}
    return render(request, "configTemplates/configure_action.html", context)


def define_template(request):
    action_provider_name = request.POST["action_provider"]
    options = action_provider.get_options_for_provider(action_provider_name)
    configured_options = dict()
    for opt in options:
        if opt["name"] in request.POST:
            o = dict()
            o["name"] = opt["name"]
            o["value"] = request.POST[opt["name"]]
            o["label"] = opt["label"]
            configured_options[o["name"]] = o
        else:
            context = {"error": "Required option not found in request!"}
            return render(request, "error.html", context)

    print "Setting configured options to the session %s" % configured_options
    request.session["new_template_action_options"] = configured_options
    context = {"options": configured_options, "action_provider": action_provider_name}
    return render(request, "configTemplates/define_template.html", context)


def new_template(request):

    action_providers = action_provider.get_action_provider_select()

    template_form = ConfigTemplateForm()
    template_form.fields["action_provider"].choices = action_providers
    context = {"template_form": template_form, "action_providers": action_providers}
    return render(request, "configTemplates/new.html", context)


def get_options_for_action(request):
    action_name = request.POST["action_name"]
    print action_name
    for a in settings.ACTION_PROVIDERS:
        print a
        if a["name"] == action_name:
            return HttpResponse(json.dumps(a), content_type="application/json")


def edit(request, template_id):
    template = get_object_or_404(ConfigTemplate, pk=template_id)

    default_options = action_provider.get_options_for_provider(template.action_provider)
    action_options = json.loads(template.action_provider_options)

    context = {"template": template, "action_options": json.dumps(action_options), "default_options": default_options}
    return render(request, "configTemplates/edit.html", context)


def update(request):
    try:
        print "HERE WE GO"
        if "id" in request.POST:
            template_id = request.POST["id"]
            template = get_object_or_404(ConfigTemplate, pk=template_id)
            template.name = request.POST["name"]
            template.description = request.POST["description"]
            template.template = request.POST["template"]

            options = action_provider.get_options_for_provider(template.action_provider)
            configured_options = dict()
            for opt in options:
                print "Checking %s" % opt["name"]
                if opt["name"] in request.POST:
                    o = dict()
                    o["name"] = opt["name"]
                    o["value"] = request.POST[opt["name"]]
                    o["label"] = opt["label"]
                    configured_options[o["name"]] = o
                else:
                    context = {"error": "Required option not found in request!"}
                    return render(request, "error.html", context)

            template.action_provider_options = json.dumps(configured_options)
            template.save()
            return HttpResponseRedirect("/tools")
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
    template.template = request.POST["template"]
    template.type = request.POST["type"]

    if "new_template_action_options" not in request.session:
        return render(request, "error.html", {
            "error": "Invalid session data!"
        })

    configured_action_options = request.session["new_template_action_options"]
    template.action_provider_options = json.dumps(configured_action_options)

    print "Saving form"
    template.save()
    return HttpResponseRedirect("/input_forms/view_from_template/%s" % template.id)


def detail(request, template_id):
    template = get_object_or_404(ConfigTemplate, pk=template_id)
    return render(request, "configTemplates/details.html", {"template": template})


def delete(request, template_id):
    template = get_object_or_404(ConfigTemplate, pk=template_id)
    template.delete()
    return HttpResponseRedirect("/tools")


def get_template_input_parameters(request):
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
    t = get_template_from_string(config_template.template)
    input_parameters = []
    for node in t:
        defined_tags = node.get_nodes_by_type(VariableNode)
        for v in defined_tags:
            print "adding %s as an available tag" % v.filter_expression
            variable_string = str(v.filter_expression)
            if variable_string not in input_parameters:
                input_parameters.append(variable_string)

    # FIXME maybe move these to the settings.py ?
    host = request.META["HTTP_HOST"]
    url = "/api/execute_template"

    template_usage = {
        "id": config_template.id,
        "name": config_template.name,
        "description": config_template.description,
        "a_frame_url": "http://" + host + url,
        "input_parameters": input_parameters
    }

    print config_template.type

    if config_template.type == "per-endpoint":
        input_parameters.append("af_endpoint_ip")
        input_parameters.append("af_endpoint_username")
        input_parameters.append("af_endpoint_password")
        input_parameters.append("af_endpoint_type")

    return render(request, "configTemplates/overlay.html", template_usage)


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
