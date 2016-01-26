from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, HttpResponse
from django.template.base import VariableNode
from django.template.loader import get_template_from_string
from django.template import Context
from django.core.exceptions import ObjectDoesNotExist
import json
from input_forms.models import InputForm
from tools.models import ConfigTemplate
from a_frame.utils import endpoint_provider
from a_frame.utils import action_provider


def index(request):
    work_flow_list = InputForm.objects.all().order_by('modified')
    context = {'work_flow_list': work_flow_list}
    return render(request, 'input_forms/index.html', context)


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
        if input_form.script.type == 'per-endpoint':
            results.append(input_form.name)

    return HttpResponse(json.dumps(results), content_type="application/json")


def edit(request, input_form_id):
    input_form = InputForm.objects.get(pk=input_form_id)
    config_template = input_form.script
    t = get_template_from_string(config_template.template)

    print "JSON IS"
    print input_form.json
    print "END JSON"

    available_tags = []
    for node in t:
        # django template contains a list of Nodes
        # which can be used to find the user configured variables in the template
        defined_tags = node.get_nodes_by_type(VariableNode)
        for v in defined_tags:
            print "adding %s as an available tag" % v.filter_expression
            variable_string = str(v.filter_expression)
            if variable_string not in available_tags:
                available_tags.append(variable_string)

    context = {'input_form': input_form, 'config_template': config_template, 'available_tags': available_tags}
    return render(request, 'input_forms/edit.html', context)


def detail(request, input_form_id):
    input_form = InputForm.objects.get(pk=input_form_id)
    print input_form.json
    json_object = json.loads(input_form.json)
    context = {'input_form': input_form, 'json_object': json_object}
    if input_form.script.type == "standalone":
        return render(request, 'input_forms/configure_standalone_template.html', context)
    else:
        return render(request, 'input_forms/preview.html', context)


def delete(request, input_form_id):
    input_form = get_object_or_404(InputForm, pk=input_form_id)
    input_form.delete()
    return HttpResponseRedirect('/input_forms')


def new(request):
    config_templates = ConfigTemplate.objects.all().order_by('name')
    context = {'config_templates': config_templates}
    return render(request, 'input_forms/new.html', context)


def new_from_template(request, template_id):
    print "new from template called"
    config_template = get_object_or_404(ConfigTemplate, pk=template_id)
    t = get_template_from_string(config_template.template)
    available_tags = []
    for node in t:
        defined_tags = node.get_nodes_by_type(VariableNode)
        for v in defined_tags:
            print "adding %s as an available tag" % v.filter_expression
            variable_string = str(v.filter_expression)
            if variable_string not in available_tags:
                available_tags.append(variable_string)

    context = {'config_template': config_template, 'available_tags': available_tags}
    return render(request, 'input_forms/new.html', context)


def create(request):
    required_fields = set(['config_template_id', 'name', 'description', 'json'])
    if not required_fields.issubset(request.POST):
        return render(request, 'error.html', {'error': "Invalid Parameters in POST"})

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
    return HttpResponseRedirect('/input_forms')


def update(request):
    required_fields = set(['input_form_id', 'config_template_id', 'name', 'description', 'json'])
    if not required_fields.issubset(request.POST):
        return render(request, 'error.html', {'error': "Invalid Parameters in POST"})

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
    return HttpResponseRedirect('/input_forms')


def preview(request, input_form_id):
    input_form = InputForm.objects.get(pk=input_form_id)
    print input_form.json
    json_object = json.loads(input_form.json)
    context = {'input_form': input_form, 'json_object': json_object}
    return render(request, 'input_forms/preview.html', context)


def configure_template_for_endpoint(request):
    required_fields = set(['input_form_name', 'provider', 'endpoint_id'])
    if not required_fields.issubset(request.POST):
        return render(request, 'error.html', {'error': "Invalid Parameters in POST"})

    input_form_name = request.POST["input_form_name"]
    provider = request.POST["provider"]
    endpoint_id = request.POST["endpoint_id"]

    provider_instance = endpoint_provider.get_provider_instance(provider)
    endpoint = provider_instance.get_endpoint_by_id(endpoint_id)

    input_form = InputForm.objects.get(name=input_form_name)

    print input_form.json
    json_object = json.loads(input_form.json)

    context = {'input_form': input_form, 'json_object': json_object, 'endpoint': endpoint, 'provider': provider}
    return render(request, 'input_forms/configure_per_endpoint_template.html', context)


def configure_template_for_queue(request):
    required_fields = set(['input_form_name', 'provider'])
    if not required_fields.issubset(request.POST):
        return render(request, 'error.html', {'error': "Invalid Parameters in POST"})

    input_form_name = request.POST["input_form_name"]
    provider = request.POST["provider"]
    endpoints = request.session["job_endpoints"]

    input_form = InputForm.objects.get(name=input_form_name)

    print input_form.json
    json_object = json.loads(input_form.json)

    context = {'input_form': input_form, 'json_object': json_object, 'endpoints': endpoints, 'provider': provider}
    return render(request, 'input_forms/configure_template_for_queue.html', context)


def apply_template(request):
    required_fields = set(['input_form_id', 'endpoint_id'])
    if not required_fields.issubset(request.POST):
        return render(request, 'error.html', {'error': "Invalid Parameters in POST"})

    input_form_id = request.POST["input_form_id"]
    endpoint_id = request.POST["endpoint_id"]
    provider = request.POST["provider"]

    provider_instance = endpoint_provider.get_provider_instance(provider)
    endpoint = provider_instance.get_endpoint_by_id(endpoint_id)

    print "got endpoint ok"

    input_form = InputForm.objects.get(pk=input_form_id)

    print input_form.json
    json_object = json.loads(input_form.json)

    context = Context()
    for j in json_object:
        print "setting context %s" % j["name"]
        context[j["name"]] = str(request.POST[j["name"]])

    print context

    config_template = input_form.script

    compiled_template = get_template_from_string(config_template.template)
    completed_template = str(compiled_template.render(context))

    print "TEMPLATE IS:"
    print completed_template
    action_name = config_template.action_provider
    action_options = json.loads(config_template.action_provider_options)

    print "transport name is: " + action_name

    action = action_provider.get_provider_instance(action_name, action_options)
    action.set_endpoint(endpoint)
    results = action.execute_template(completed_template)
    context = {"results": results}
    return render(request, 'input_forms/results.html', context)


def apply_standalone_template(request):
    if "input_form_id" not in request.POST:
        return render(request, 'error.html', {'error': "Invalid Parameters in POST"})

    input_form_id = request.POST["input_form_id"]

    input_form = InputForm.objects.get(pk=input_form_id)

    json_object = json.loads(input_form.json)

    context = Context()
    for j in json_object:
        print "setting context %s" % j["name"]
        context[j["name"]] = str(request.POST[j["name"]])

    config_template = input_form.script

    compiled_template = get_template_from_string(config_template.template)
    completed_template = str(compiled_template.render(context))

    print completed_template
    action_name = config_template.action_provider
    action_options = json.loads(config_template.action_provider_options)

    action = action_provider.get_provider_instance(action_name, action_options)
    results = action.execute_template(completed_template)
    context = {"results": results}
    return render(request, 'input_forms/results.html', context)


def apply_template_to_queue(request):
    if "input_form_id" not in request.POST:
        return render(request, 'error.html', {'error': "Invalid Parameters in POST"})

    input_form_id = request.POST["input_form_id"]
    endpoints = request.session["job_endpoints"]
    input_form = InputForm.objects.get(pk=input_form_id)

    print input_form.json
    json_object = json.loads(input_form.json)

    context = Context()
    for j in json_object:
        print "setting context %s" % j["name"]
        context[j["name"]] = str(request.POST[j["name"]])

    print context

    config_template = input_form.script

    compiled_template = get_template_from_string(config_template.template)
    completed_template = str(compiled_template.render(context))

    print "TEMPLATE IS:"
    print completed_template
    action_name = config_template.action_provider
    action_options = json.loads(config_template.action_provider_options)

    print "transport name is: " + action_name
    print "action options are: " + str(action_options)

    action = action_provider.get_provider_instance(action_name, action_options)

    results = ""
    for endpoint in endpoints:
        results += "================ %s ================\n" % endpoint["name"]
        action.set_endpoint(endpoint)
        result = action.execute_template(completed_template)
        results += result
        results += "\n"

    context = {"results": results}
    return render(request, 'input_forms/results.html', context)


def view_from_template(request, template_id):
    config_template = get_object_or_404(ConfigTemplate, pk=template_id)
    try:
        input_form = InputForm.objects.get(script=config_template)
        return HttpResponseRedirect('/input_forms/%s' % input_form.id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect('/input_forms/new/%s' % template_id)


def edit_from_template(request, template_id):
    config_template = get_object_or_404(ConfigTemplate, pk=template_id)
    try:
        input_form = InputForm.objects.get(script=config_template)
        return HttpResponseRedirect('/input_forms/edit/%s' % input_form.id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect('/input_forms/new/%s' % template_id)