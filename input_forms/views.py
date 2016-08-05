from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, HttpResponse
from django.template.base import VariableNode
from django.template import engines
from django.template import Context
from django.template import TemplateSyntaxError
from django.core.exceptions import ObjectDoesNotExist
import json
import re
from urllib import quote, unquote
from input_forms.models import InputForm
from input_forms.forms import ImportForm
from tools.models import ConfigTemplate
from a_frame.utils import action_provider
from endpoints import endpoint_provider
from common.lib import aframe_utils


def index(request):
    input_form_list = InputForm.objects.all().order_by("name")
    context = {"input_form_list": input_form_list}
    return render(request, "input_forms/index.html", context)


def search(request):
    """
    used for UI autocomplete searches. Only used on the endpoint details page. Filter out standalone type templates
    :param request:
    :return:
    """
    term = request.GET["term"]
    input_form_list = InputForm.objects.filter(name__contains=term)
    results = []
    for input_form in input_form_list:
        if input_form.script.type == "per-endpoint":
            results.append(input_form.name)

    return HttpResponse(json.dumps(results), content_type="application/json")


def edit(request, input_form_id):
    input_form = InputForm.objects.get(pk=input_form_id)
    config_template = input_form.script

    try:
        t = engines['django'].from_string(config_template.template)
    except TemplateSyntaxError as e:
        print "Caught a template syntax error!"
        return render(request, "error.html", {"error": "Invalid Template Syntax: %s" % str(e)})

    print "JSON IS"
    print input_form.json
    print "END JSON"

    available_tags = []
    for node in t.template.nodelist:
        # django template contains a list of Nodes
        # which can be used to find the user configured variables in the template
        defined_tags = node.get_nodes_by_type(VariableNode)
        for v in defined_tags:
            print "adding %s as an available tag" % v.filter_expression
            variable_string = str(v.filter_expression)
            if variable_string not in available_tags:
                if not variable_string.startswith("af_"):
                    available_tags.append(variable_string)

    context = {"input_form": input_form, "config_template": config_template, "available_tags": available_tags}
    return render(request, "input_forms/edit.html", context)


def detail(request, input_form_id):
    input_form = InputForm.objects.get(pk=input_form_id)
    print input_form.json
    json_object = json.loads(input_form.json)

    config_template = input_form.script
    action_options = json.loads(config_template.action_provider_options)

    context = {"input_form": input_form, "json_object": json_object, 'action_options': action_options}
    if input_form.script.type == "standalone":
        return render(request, "input_forms/configure_standalone_template.html", context)
    else:
        return render(request, "input_forms/preview.html", context)


def delete(request, input_form_id):
    input_form = get_object_or_404(InputForm, pk=input_form_id)
    input_form.delete()
    return HttpResponseRedirect("/input_forms")


def new(request):
    config_templates = ConfigTemplate.objects.all().order_by("name")
    context = {"config_templates": config_templates}
    return render(request, "input_forms/new.html", context)


def new_from_template(request, template_id):
    print "new from template called"
    config_template = get_object_or_404(ConfigTemplate, pk=template_id)
    try:
        t = engines['django'].from_string(config_template.template)
    except TemplateSyntaxError as e:
        print "Caught a template syntax error!"
        return render(request, "error.html", {"error": "Invalid Template Syntax: %s" % str(e)})

    available_tags = []

    for node in t.template.nodelist:
        defined_tags = node.get_nodes_by_type(VariableNode)
        for v in defined_tags:
            print "adding %s as an available tag" % v.filter_expression
            variable_string = str(v.filter_expression)
            if variable_string not in available_tags:
                if not variable_string.startswith("af_"):
                    available_tags.append(variable_string)

    context = {"config_template": config_template, "available_tags": available_tags}
    return render(request, "input_forms/new.html", context)


def create(request):
    required_fields = set(["config_template_id", "name", "description", "json"])
    if not required_fields.issubset(request.POST):
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    template_id = request.POST["config_template_id"]
    name = request.POST["name"]
    description = request.POST["description"]
    json_data = request.POST["json"]
    instructions = request.POST["instructions"]

    config_template = get_object_or_404(ConfigTemplate, pk=template_id)

    input_form = InputForm()
    input_form.name = name
    input_form.description = description
    input_form.instructions = instructions
    input_form.json = json_data
    input_form.script = config_template
    input_form.save()
    return HttpResponseRedirect("/input_forms")


def export_form(request, input_form_id):
    print "exporting %s" % input_form_id
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

    print json.dumps(exported_object)

    response = HttpResponse(json.dumps(exported_object), content_type="application/json")
    response['Content-Disposition'] = 'attachment; filename=' + 'aframe-' + str(config_template.name) + '.json'

    return response


def import_form(request):
    if request.method == "POST":
        json_file = request.FILES['file']
        json_string = json_file.read()
        json_data = json.loads(json_string)

        template_options = json_data["template"]
        form_options = json_data["form"]

        template = ConfigTemplate()
        template.name = template_options["name"]
        template.description = template_options["description"]
        template.action_provider = template_options["action_provider"]
        template.action_provider_options = template_options["action_provider_options"]
        template.type = template_options["type"]
        template.template = unquote(template_options["template"])

        template.save()

        input_form = InputForm()
        input_form.name = form_options["name"]
        input_form.description = form_options["description"]
        input_form.instuctions = form_options["instructions"]
        input_form.json = unquote(form_options["json"])
        input_form.script = template

        input_form.save()

        return HttpResponseRedirect("/input_forms")
    else:
        form = ImportForm()
        context = {'form': form }
        return render(request, 'input_forms/import.html', context)


def update(request):
    required_fields = set(["input_form_id", "config_template_id", "name", "description", "json"])
    if not required_fields.issubset(request.POST):
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    input_form_id = request.POST["input_form_id"]
    template_id = request.POST["config_template_id"]
    name = request.POST["name"]
    description = request.POST["description"]
    json_data = request.POST["json"]
    instructions = request.POST["instructions"]

    input_form = get_object_or_404(InputForm, pk=input_form_id)
    config_template = get_object_or_404(ConfigTemplate, pk=template_id)

    input_form.id = input_form_id
    input_form.name = name
    input_form.description = description
    input_form.instructions = instructions
    input_form.json = json_data
    input_form.script = config_template
    input_form.save()
    return HttpResponseRedirect("/input_forms")


def preview(request, input_form_id):
    input_form = InputForm.objects.get(pk=input_form_id)
    print input_form.json
    json_object = json.loads(input_form.json)
    context = {"input_form": input_form, "json_object": json_object}
    return render(request, "input_forms/preview.html", context)


def configure_template_for_endpoint(request):
    required_fields = set(["input_form_name", "group_id", "endpoint_id"])
    if not required_fields.issubset(request.POST):
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    input_form_name = request.POST["input_form_name"]
    group_id = request.POST["group_id"]
    endpoint_id = request.POST["endpoint_id"]

    print endpoint_id

    provider_instance = endpoint_provider.get_provider_instance_from_group(group_id)
    endpoint = provider_instance.get_endpoint_by_id(endpoint_id)

    input_form = InputForm.objects.get(name=input_form_name)

    print input_form.json
    json_object = json.loads(input_form.json)

    config_template = input_form.script
    action_options = json.loads(config_template.action_provider_options)

    context = {"input_form": input_form, "json_object": json_object, "endpoint": endpoint, "group_id": group_id,
               'action_options' : action_options
               }
    return render(request, "input_forms/configure_per_endpoint_template.html", context)


def configure_template_for_queue(request):
    required_fields = set(["input_form_name", "group_id"])
    if not required_fields.issubset(request.POST):
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    input_form_name = request.POST["input_form_name"]
    group_id = request.POST["group_id"]
    endpoints = request.session["endpoint_queue"]

    input_form = InputForm.objects.get(name=input_form_name)

    print input_form.json
    json_object = json.loads(input_form.json)

    context = {"input_form": input_form, "json_object": json_object, "endpoints": endpoints, "group_id": group_id}
    return render(request, "input_forms/configure_template_for_queue.html", context)


def apply_template(request):
    """

    :param request: HTTPRequest from the input form
    :return: results of the template execution

    """

    required_fields = set(["input_form_id", "endpoint_id", "group_id"])
    if not required_fields.issubset(request.POST):
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    input_form_id = request.POST["input_form_id"]
    endpoint_id = request.POST["endpoint_id"]
    group_id = request.POST["group_id"]

    provider_instance = endpoint_provider.get_provider_instance_from_group(group_id)
    endpoint = provider_instance.get_endpoint_by_id(endpoint_id)

    if "username" not in endpoint or endpoint["username"] == "":
        if "global_username" in request.POST:
            endpoint["username"] = request.POST["global_username"]
        else:
            raise Exception("Authentication is required!")

    if "password" not in endpoint or endpoint["password"] == "":
        if "global_password" in request.POST:
            endpoint["password"] = request.POST["global_password"]
        else:
            raise Exception("Authentication is required!")

    input_form = InputForm.objects.get(pk=input_form_id)

    print input_form.json
    json_object = json.loads(input_form.json)

    context = Context()
    for j in json_object:
        if '.' in j["name"]:
            # this is a json capable variable name
            j_dict = aframe_utils.generate_dict(j["name"], str(request.POST[j["name"]]))
            context.update(j_dict)
        else:
            print "setting context %s" % j["name"]
            context[j["name"]] = str(request.POST[j["name"]])

    context["af_endpoint_ip"] = endpoint["ip"]
    context["af_endpoint_username"] = endpoint["username"]
    context["af_endpoint_password"] = endpoint["password"]
    context["af_endpoint_type"] = endpoint["type"]

    print context

    config_template = input_form.script

    try:
        compiled_template = engines['django'].from_string(config_template.template)
        completed_template = str(compiled_template.render(context))
    except TemplateSyntaxError as e:
        print "Caught a template syntax error!"
        return render(request, "error.html", {"error": "Invalid Template Syntax: %s" % str(e)})

    print "TEMPLATE IS:"
    print completed_template
    action_name = config_template.action_provider
    action_options = json.loads(config_template.action_provider_options)

    print "action name is: " + action_name

    action = action_provider.get_provider_instance(action_name, action_options)
    action.set_endpoint(endpoint)
    results = action.execute_template(completed_template)
    context = {"results": results}
    return render(request, "input_forms/results.html", context)


def apply_standalone_template(request):
    if "input_form_id" not in request.POST:
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    input_form_id = request.POST["input_form_id"]

    input_form = InputForm.objects.get(pk=input_form_id)

    json_object = json.loads(input_form.json)

    context = Context()
    for j in json_object:
        if '.' in j["name"]:
            print j
            # this is a fancy variable name
            j_dict = aframe_utils.generate_dict(j["name"], str(request.POST[j["name"]]))
            print j_dict
            context.update(j_dict)
        else:
            print "setting context %s" % j["name"]
            context[j["name"]] = str(request.POST[j["name"]])

    config_template = input_form.script

    try:
        compiled_template = engines['django'].from_string(config_template.template)
    except TemplateSyntaxError as e:
        print "Caught a template syntax error!"
        return render(request, "error.html", {"error": "Invalid Template Syntax: %s" % str(e)})

    completed_template = str(compiled_template.render(context))

    print completed_template
    action_name = config_template.action_provider
    print action_name

    action_options = json.loads(config_template.action_provider_options)
    print action_options

    for ao in action_options:
        if "action_options_" + str(ao) in request.POST:
            print "Found a customized action option!"
            new_val = request.POST["action_options_" + str(ao)]
            current_value = action_options[ao]["value"]
            action_options[ao]["value"] = re.sub("{{ .* }}", new_val, current_value)
            print action_options[ao]["value"]

    action = action_provider.get_provider_instance(action_name, action_options)
    results = action.execute_template(completed_template)
    context = {"results": results}
    return render(request, "input_forms/results.html", context)


def apply_template_to_queue(request):
    if "input_form_id" not in request.POST:
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    input_form_id = request.POST["input_form_id"]
    endpoints = request.session["endpoint_queue"]
    input_form = InputForm.objects.get(pk=input_form_id)

    print input_form.json
    json_object = json.loads(input_form.json)

    context = Context()
    for j in json_object:
        if '.' in j["name"]:
            # this is a json capable variable name
            j_dict = aframe_utils.generate_dict(j["name"], str(request.POST[j["name"]]))
            context.update(j_dict)
        else:
            print "setting context %s" % j["name"]
            context[j["name"]] = str(request.POST[j["name"]])

    print context

    config_template = input_form.script

    try:
        compiled_template = engines['django'].from_string(config_template.template)
    except TemplateSyntaxError as e:
        print "Caught a template syntax error!"
        return render(request, "error.html", {"error": "Invalid Template Syntax: %s" % str(e)})

    action_name = config_template.action_provider
    action_options = json.loads(config_template.action_provider_options)

    print "action name is: " + action_name
    print "action options are: " + str(action_options)

    action = action_provider.get_provider_instance(action_name, action_options)

    results = ""
    for endpoint in endpoints:
        if "username" not in endpoint or endpoint["username"] == "":
            if "global_username" in request.POST:
                endpoint["username"] = request.POST["global_username"]
            else:
                raise Exception("Authentication is required!")

        if "password" not in endpoint or endpoint["password"] == "":
            if "global_password" in request.POST:
                endpoint["password"] = request.POST["global_password"]
            else:
                raise Exception("Authentication is required!")

        context["af_endpoint_ip"] = endpoint["ip"]
        context["af_endpoint_username"] = endpoint["username"]
        context["af_endpoint_password"] = endpoint["password"]
        context["af_endpoint_type"] = endpoint["type"]

        completed_template = str(compiled_template.render(context))

        results += "================ %s ================\n" % endpoint["name"]
        action.set_endpoint(endpoint)
        result = action.execute_template(completed_template)
        results += result
        results += "\n"

    context = {"results": results}
    return render(request, "input_forms/results.html", context)


def view_from_template(request, template_id):
    config_template = get_object_or_404(ConfigTemplate, pk=template_id)
    try:
        input_form = InputForm.objects.get(script=config_template)
        return HttpResponseRedirect("/input_forms/%s" % input_form.id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect("/input_forms/new/%s" % template_id)


def edit_from_template(request, template_id):
    config_template = get_object_or_404(ConfigTemplate, pk=template_id)
    try:
        input_form = InputForm.objects.get(script=config_template)
        return HttpResponseRedirect("/input_forms/edit/%s" % input_form.id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect("/input_forms/new/%s" % template_id)
