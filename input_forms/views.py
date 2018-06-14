import json
import logging
import re
from urllib import quote, unquote

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, HttpResponse
from django.template import TemplateSyntaxError, TemplateDoesNotExist
from django.template import engines
from django.template.base import VariableNode

from a_frame import settings
from a_frame.utils import action_provider
from common.lib import aframe_utils
from endpoints import endpoint_provider
from input_forms.forms import ImportForm
from input_forms.models import InputForm
from tools.models import ConfigTemplate

logger = logging.getLogger(__name__)


def index(request):
    logger.info("__ input_forms index __")
    input_form_list = InputForm.objects.all().order_by("name")
    context = {"input_form_list": input_form_list}
    return render(request, "input_forms/index.html", context)


def search(request):
    """
    used for UI autocomplete searches. Only used on the endpoint details page. Filter out standalone type templates
    :param request:
    :return:
    """
    logger.info("__ input_forms search __")

    term = request.GET["term"]
    input_form_list = InputForm.objects.filter(name__contains=term)
    results = []
    for input_form in input_form_list:
        if input_form.script.type == "per-endpoint":
            r = dict()
            r["value"] = input_form.id
            r["label"] = input_form.name
            results.append(r)

    return HttpResponse(json.dumps(results), content_type="application/json")


def search_all(request):
    """
    used for UI autocomplete searches. No filtering is applied, also returns dicts instead of a simple list of names
    :param request: term
    :return: json list of dicts
    """
    logger.info("__ input_forms search __")

    term = request.GET["term"]
    input_form_list = InputForm.objects.filter(name__contains=term)
    results = []
    for input_form in input_form_list:
        r = dict()
        r["value"] = input_form.id
        r["label"] = input_form.name
        results.append(r)

    return HttpResponse(json.dumps(results), content_type="application/json")


def search_standalone(request):
    """
    used for UI autocomplete searches. Filter out per-endpoint type templates
    :param request:
    :return:
    """
    logger.info("__ input_forms search_standalone __")

    term = request.GET["term"]
    input_form_list = InputForm.objects.filter(name__contains=term)
    results = []
    for input_form in input_form_list:
        if input_form.script.type == "standalone":
            r = dict()
            r["value"] = input_form.id
            r["label"] = input_form.name
            results.append(r)

    return HttpResponse(json.dumps(results), content_type="application/json")


def edit(request, input_form_id):
    logger.info("__ input_forms edit __")
    input_form = InputForm.objects.get(pk=input_form_id)
    config_template = input_form.script

    try:
        t = engines['django'].from_string(config_template.template)
    except TemplateSyntaxError as e:
        logger.error("Caught a template syntax error!")
        return render(request, "error.html", {"error": "Invalid Template Syntax: %s" % str(e)})

    logger.debug(input_form.json)

    available_tags = []
    for node in t.template.nodelist:
        # django template contains a list of Nodes
        # which can be used to find the user configured variables in the template
        defined_tags = node.get_nodes_by_type(VariableNode)
        for v in defined_tags:
            logger.info("adding %s as an available tag" % v.filter_expression)
            variable_string = str(v.filter_expression)
            if variable_string not in available_tags:
                if not variable_string.startswith("af_"):
                    available_tags.append(variable_string)

    widgets = settings.WIDGETS
    widgets_json = json.dumps(widgets)
    context = {
        "input_form": input_form,
        "config_template": config_template,
        "available_tags": available_tags,
        "widgets": widgets,
        "widgets_json": widgets_json
    }
    return render(request, "input_forms/edit.html", context)


def detail(request, input_form_id):
    logger.info("__ input_forms detail __")
    try:
        input_form = InputForm.objects.get(pk=input_form_id)

    except ObjectDoesNotExist as odne:
        logger.error("Input form with id %s could not be found!" % input_form_id)
        return HttpResponseRedirect("/input_forms")

    logger.debug(input_form.json)
    json_object = json.loads(input_form.json)

    for j in json_object:
        if "widget" in j:
            # modify widget options in place
            _configure_widget_options(j)

        else:
            j["widget"] = "text_input"

    config_template = input_form.script
    action_options = json.loads(config_template.action_provider_options)

    inline_per_endpoint = False

    context = {"input_form": input_form, "json_object": json_object, 'action_options': action_options,
               'inline_per_endpoint': inline_per_endpoint}

    if input_form.script.type == "standalone":
        return render(request, "input_forms/configure_standalone_template.html", context)
    else:
        return render(request, "input_forms/preview.html", context)


def delete(request, input_form_id):
    logger.info("__ input_forms delete __")
    input_form = get_object_or_404(InputForm, pk=input_form_id)
    input_form.delete()
    return HttpResponseRedirect("/input_forms")


def new(request):
    logger.info("__ input_forms new __")
    config_templates = ConfigTemplate.objects.all().order_by("name")
    context = {"config_templates": config_templates}
    return render(request, "input_forms/new.html", context)


def new_from_template(request, template_id):
    logger.info("__ input_forms new_from_template __")
    config_template = get_object_or_404(ConfigTemplate, pk=template_id)
    try:
        t = engines['django'].from_string(config_template.template)
    except TemplateSyntaxError as e:
        logger.error("Caught a template syntax error!")
        return render(request, "error.html", {"error": "Invalid Template Syntax: %s" % str(e)})

    available_tags = []

    for node in t.template.nodelist:
        defined_tags = node.get_nodes_by_type(VariableNode)
        for v in defined_tags:
            logger.info("adding %s as an available tag" % v.filter_expression)
            variable_string = str(v.filter_expression)
            if variable_string not in available_tags:
                if not variable_string.startswith("af_"):
                    available_tags.append(variable_string)
    widgets = settings.WIDGETS
    widgets_json = json.dumps(widgets)
    context = {
        "config_template": config_template,
        "available_tags": available_tags,
        "widgets": widgets,
        "widgets_json": widgets_json
    }

    if 'cloned_templates' in request.session:
        print 'found cloned templates'
        cloned_templates = request.session['cloned_templates']
        if template_id in cloned_templates:
            print 'found this template_id'
            if 'input_form_id' in cloned_templates[template_id]:
                cloned_input_form_id = cloned_templates[template_id]['input_form_id']
                try:
                    input_form = InputForm.objects.get(pk=cloned_input_form_id)
                    dolly = InputForm()
                    dolly.name = config_template.name
                    dolly.description = config_template.description
                    dolly.instructions = input_form.instructions
                    dolly.json = input_form.json
                    dolly.script = config_template
                    dolly.save()
                    context['input_form'] = dolly
                    return render(request, "input_forms/edit.html", context)
                except ObjectDoesNotExist:
                    print 'Could not find the input for for this cloned template'

    else:
        print 'no cloned templates found!'

    return render(request, "input_forms/new.html", context)


def create(request):
    logger.info("__ input_forms create __")
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
    logger.info("__ input_forms export_form __")
    logger.info("exporting %s" % input_form_id)

    exported_json = aframe_utils.export_input_form(input_form_id)

    input_form = InputForm.objects.get(pk=input_form_id)
    config_template = input_form.script
    #
    # template_options = dict()
    # template_options["name"] = config_template.name
    # template_options["description"] = config_template.description
    # template_options["action_provider"] = config_template.action_provider
    # template_options["action_provider_options"] = config_template.action_provider_options
    # template_options["type"] = config_template.type
    # template_options["template"] = quote(config_template.template)
    #
    # form_options = dict()
    # form_options["name"] = input_form.name
    # form_options["description"] = input_form.description
    # form_options["instructions"] = input_form.instructions
    # form_options["json"] = quote(input_form.json)
    #
    # exported_object = dict()
    # exported_object["template"] = template_options
    # exported_object["form"] = form_options
    #
    # logger.debug(json.dumps(exported_object))

    # response = HttpResponse(json.dumps(exported_object), content_type="application/json")

    response = HttpResponse(exported_json, content_type="application/json")
    response['Content-Disposition'] = 'attachment; filename=' + 'aframe-' + str(config_template.name) + '.json'

    return response


def import_form(request):
    logger.info("__ input_forms import_form __")
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
        input_form.instructions = form_options["instructions"]
        input_form.json = unquote(form_options["json"])
        input_form.script = template

        input_form.save()

        return HttpResponseRedirect("/input_forms")
    else:
        form = ImportForm()
        context = {'form': form}
        return render(request, 'input_forms/import.html', context)


def update(request):
    logger.info("__ input_forms update __")
    required_fields = set(["input_form_id", "config_template_id", "name", "description", "json"])
    if not required_fields.issubset(request.POST):
        logger.error("Did no find all required fields in request")
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
    logger.info("__ input_forms preview __")
    input_form = InputForm.objects.get(pk=input_form_id)
    logger.debug(input_form.json)
    json_object = json.loads(input_form.json)
    context = {"input_form": input_form, "json_object": json_object}
    return render(request, "input_forms/preview.html", context)


def configure_template_for_screen(request, input_form_id):
    logger.info("__ input_forms configure_template_for_screen __")
    input_form = InputForm.objects.get(pk=input_form_id)
    logger.debug(input_form.json)
    json_object = list()
    json_object = json.loads(input_form.json)
    for jo in json_object:
        if "widget" in jo:
            _configure_widget_options(jo)
        else:
            jo["widget"] = "text_input"

    config_template = input_form.script
    action_options = json.loads(config_template.action_provider_options)

    inline_per_endpoint = False
    if config_template.type == 'per-endpoint':
        inline_per_endpoint = True

    context = {"input_form": input_form, "json_object": json_object, 'action_options': action_options,
               'inline_per_endpoint': inline_per_endpoint}

    return render(request, "input_forms/configure_template_for_inline.html", context)


def configure_template_for_endpoint(request):
    logger.info("__ input_forms confgure_template_for_endpoint __")
    required_fields = set(["input_form_name", "group_id", "endpoint_id"])
    if not required_fields.issubset(request.POST):
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    input_form_name = request.POST["input_form_name"]
    group_id = request.POST["group_id"]
    endpoint_id = request.POST["endpoint_id"]

    logger.debug("Configuring template for endpoint: %s" % endpoint_id)

    provider_instance = endpoint_provider.get_provider_instance_from_group(group_id)
    endpoint = provider_instance.get_endpoint_by_id(endpoint_id)

    input_form = InputForm.objects.get(name=input_form_name)

    logger.debug(input_form.json)
    json_object = json.loads(input_form.json)
    for jo in json_object:
        if "widget" in jo:
            _configure_widget_options(jo)
        else:
            jo["widget"] = "text_input"

    config_template = input_form.script
    action_options = json.loads(config_template.action_provider_options)

    context = {"input_form": input_form, "json_object": json_object, "endpoint": endpoint, "group_id": group_id,
               'action_options': action_options
               }
    return render(request, "input_forms/configure_per_endpoint_template.html", context)


def configure_template_for_queue(request):
    logger.info("__ input_forms configure_template_for_queue __")
    required_fields = set(["input_form_name", "group_id"])
    if not required_fields.issubset(request.POST):
        logger.error("Did no find all required fields in request")
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    input_form_name = request.POST["input_form_name"]
    group_id = request.POST["group_id"]
    endpoints = request.session["endpoint_queue"]

    input_form = InputForm.objects.get(name=input_form_name)

    logger.debug(input_form.json)
    json_object = json.loads(input_form.json)
    for jo in json_object:
        if "widget" in jo:
            _configure_widget_options(jo)
        else:
            jo["widget"] = "text_input"

    context = {"input_form": input_form, "json_object": json_object, "endpoints": endpoints, "group_id": group_id}
    return render(request, "input_forms/configure_template_for_queue.html", context)


def apply_per_endpoint_template(request):
    """

    :param request: HTTPRequest from the input form
    :return: results of the template execution

    """
    logger.info("__ input_forms apply_per_endpoint_template __")

    required_fields = set(["input_form_id", "endpoint_id", "group_id"])
    if not required_fields.issubset(request.POST):
        logger.error("Did no find all required fields in request")
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

    logger.debug(input_form.json)
    json_object = json.loads(input_form.json)

    context = dict()
    for j in json_object:
        if '.' in j["name"]:
            # this is a json capable variable name
            j_dict = aframe_utils.generate_dict(j["name"], str(request.POST.get(j["name"], '')))
            context.update(j_dict)
        else:
            logger.debug("setting context %s" % j["name"])
            # don't worry about null values here
            context[j["name"]] = str(request.POST.get(j['name'], ''))

    context["af_endpoint_ip"] = endpoint["ip"]
    context["af_endpoint_id"] = endpoint["id"]
    context["af_endpoint_name"] = endpoint["name"]
    context["af_endpoint_username"] = endpoint["username"]
    context["af_endpoint_password"] = endpoint["password"]
    context["af_endpoint_type"] = endpoint["type"]

    logger.debug(context)

    config_template = input_form.script

    try:
        compiled_template = engines['django'].from_string(config_template.template)
        completed_template = str(compiled_template.render(context))
    except TemplateSyntaxError as e:
        logger.error("Caught a template syntax error!")
        return render(request, "error.html", {"error": "Invalid Template Syntax: %s" % str(e)})

    logger.debug(completed_template)
    action_name = config_template.action_provider

    action_options = json.loads(config_template.action_provider_options)
    logger.debug(action_options)

    for ao in action_options:
        if "action_options_" + str(ao) in request.POST:
            logger.debug("Found a customized action option!")
            new_val = request.POST["action_options_" + str(ao)]
            current_value = action_options[ao]["value"]
            action_options[ao]["value"] = re.sub("{{.*}}", new_val, current_value)
            logger.debug(action_options[ao]["value"])

    logger.debug("action name is: " + action_name)

    # let's load any secrets if necessary
    provider_options = action_provider.get_options_for_provider(action_name)
    for opt in provider_options:
        print opt
        if opt['type'] == 'secret':
            opt_name = opt['name']
            pw_lookup_key = action_options[opt_name]['value']
            pw_lookup_value = aframe_utils.lookup_secret(pw_lookup_key)
            action_options[opt_name]['value'] = pw_lookup_value

    action = action_provider.get_provider_instance(action_name, action_options)
    action.set_endpoint(endpoint)
    results = action.execute_template(completed_template)
    context = {"results": results}

    if "inline" in request.POST and request.POST["inline"] == 'yes_please':
        print "returning INLINE"
        context["input_form_name"] = input_form.name
        context["input_form_id"] = input_form_id
        return render(request, "overlay_results.html", context)

    return render(request, "input_forms/results.html", context)


def apply_standalone_template(request):
    logger.info("__ input_forms apply_standalone_template __")
    if "input_form_id" not in request.POST:
        logger.error("Did no find all required fields in request")
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    input_form_id = request.POST["input_form_id"]

    input_form = InputForm.objects.get(pk=input_form_id)

    json_object = json.loads(input_form.json)

    context = dict()
    for j in json_object:
        if '.' in j["name"]:
            # this is a fancy variable name
            j_dict = aframe_utils.generate_dict(j["name"], str(request.POST[j["name"]]))
            context.update(j_dict)
        else:
            logger.debug("setting context %s" % j["name"])
            print 'setting context %s' % j['name']
            context[j["name"]] = str(request.POST[j["name"]])

    config_template = input_form.script

    try:
        compiled_template = engines['django'].from_string(config_template.template)
    except TemplateSyntaxError as e:
        logger.error("Caught a template syntax error!")
        logger.error(str(e))
        return render(request, "error.html", {"error": "Invalid Template Syntax: %s" % str(e)})

    completed_template = str(compiled_template.render(context))

    if "preview" in request.POST:
        if request.POST["preview"] == "yes_please":
            logger.info("Returning template Preview")
            pre_tags = "<html><body><pre>"
            post_tags = "</pre></body</html>"
            return HttpResponse(pre_tags + completed_template + post_tags)

    logger.info(completed_template)
    action_name = config_template.action_provider
    logger.info(action_name)

    action_options = json.loads(config_template.action_provider_options)
    logger.info(action_options)

    for ao in action_options:
        if "action_options_" + str(ao) in request.POST:
            logger.debug("Found a customized action option!")
            new_val = request.POST["action_options_" + str(ao)]
            print new_val
            current_value = action_options[ao]["value"]
            print current_value
            action_options[ao]["value"] = re.sub("{{ .* }}", new_val, current_value)
            logger.debug(action_options[ao]["value"])

    # let's load any secrets if necessary
    provider_options = action_provider.get_options_for_provider(action_name)
    for opt in provider_options:
        print opt
        if opt['type'] == 'secret':
            opt_name = opt['name']
            pw_lookup_key = action_options[opt_name]['value']
            pw_lookup_value = aframe_utils.lookup_secret(pw_lookup_key)
            action_options[opt_name]['value'] = pw_lookup_value

    print "action name is: " + action_name

    action = action_provider.get_provider_instance(action_name, action_options)
    results = action.execute_template(completed_template)
    print type(results)
    # the action is passing back extra information about the type of response
    if type(results) is dict:
        if 'display_inline' in results and results['display_inline'] is False:
            if 'cache_key' in results:
                # set extra data on the context so we can use it to build a download link downstream
                context = {
                    'results': 'Binary data',
                    'cache_key': results['cache_key'],
                    'scheme': request.scheme,
                    'host': request.get_host()
                }
        else:
            # fixme to ensure contents is always present in results when display_inline is true
            # results['content'] is currently unimplemented!
            context = {'results': results['contents']}

    else:
        # results is just a string object, so send it through
        context = {"results": results}

    if "inline" in request.POST and request.POST["inline"] == 'yes_please':
        print "returning INLINE"
        context["input_form_name"] = input_form.name
        context["input_form_id"] = input_form_id
        return render(request, "overlay_results.html", context)
    else:
        print "returning full results"
        return render(request, "input_forms/results.html", context)


def apply_template_to_queue(request):
    logger.info("__ input_forms apply_template_to_queue __")
    if "input_form_id" not in request.POST:
        logger.error("Did no find all required fields in request")
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    input_form_id = request.POST["input_form_id"]
    endpoints = request.session["endpoint_queue"]
    input_form = InputForm.objects.get(pk=input_form_id)

    logger.debug(input_form.json)
    json_object = json.loads(input_form.json)

    context = dict()
    for j in json_object:
        if '.' in j["name"]:
            # this is a json capable variable name
            j_dict = aframe_utils.generate_dict(j["name"], str(request.POST[j["name"]]))
            context.update(j_dict)
        else:
            logger.debug("setting context %s" % j["name"])
            context[j["name"]] = str(request.POST[j["name"]])

    logger.debug(context)

    config_template = input_form.script

    try:
        compiled_template = engines['django'].from_string(config_template.template)
    except TemplateSyntaxError as e:
        logger.error("Caught a template syntax error!")
        logger.error(str(e))
        return render(request, "error.html", {"error": "Invalid Template Syntax: %s" % str(e)})

    action_name = config_template.action_provider
    action_options = json.loads(config_template.action_provider_options)

    logger.debug("action name is: %s" % action_name)
    logger.debug("action options are: %s" % action_options)

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
    logger.info("__ input_forms view_from_template __")
    config_template = get_object_or_404(ConfigTemplate, pk=template_id)
    try:
        input_form = InputForm.objects.get(script=config_template)
        return HttpResponseRedirect("/input_forms/%s" % input_form.id)
    except ObjectDoesNotExist:
        logger.info("requested object id does not exist")
        return HttpResponseRedirect("/input_forms/new/%s" % template_id)


def edit_from_template(request, template_id):
    logger.info("__ input_forms edit_from_template __")
    config_template = get_object_or_404(ConfigTemplate, pk=template_id)
    try:
        input_form = InputForm.objects.get(script=config_template)
        return HttpResponseRedirect("/input_forms/edit/%s" % input_form.id)
    except ObjectDoesNotExist:
        logger.info("requested object id does not exist")
        return HttpResponseRedirect("/input_forms/new/%s" % template_id)


def load_widget_config(request):
    """
    Load the configuration for a given widget
    :param request: http request
    :return: html template
    """
    logger.info("__ input_forms load_widget_config __")
    required_fields = set(["widget_id", "target_id"])
    if not required_fields.issubset(request.POST):
        logger.error("Did no find all required fields in request")
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    widget_id = request.POST["widget_id"]
    target_id = request.POST["target_id"]

    widgets = settings.WIDGETS
    widget_name = ""
    widget_configuration_template = ""

    found = False
    for w in widgets:
        logger.debug(w["id"] + " == " + widget_id)

        if w["id"] == widget_id:
            widget_name = w["label"]
            widget_configuration_template = w["configuration_template"]
            logger.debug(widget_configuration_template)
            found = True
            break

    if not found:
        return render(request, "input_forms/widgets/overlay_error.html",
                      {"error": "Could not find widget configuration"})

    try:
        context = {"widget_id": widget_id, "widget_name": widget_name, "target_id": target_id}
        return render(request, "input_forms/widgets/%s" % widget_configuration_template, context)
    except TemplateDoesNotExist:
        return render(request, "input_forms/widgets/overlay_error.html",
                      {"error": "Could not load widget configuration"})


def _configure_widget_options(j):
    '''
    Configures widget specific options if necessary
    :param j: input_form configuration object
    :return: configured input_form json object
    '''

    if "widget_config" in j:
        logger.debug("jsonifying widget config")
        j["widget_config_json"] = json.dumps(j["widget_config"])

    if j["widget"] == "preload_list" and "widget_config" in j:

        try:
            widget_config = j["widget_config"]
            template_name = widget_config["template_name"]
            key = widget_config["key_name"]
            value = widget_config["value_name"]
            config_template = ConfigTemplate.objects.get(name=template_name)

        except (ObjectDoesNotExist, KeyError):
            logger.error('Could not load preloaded_list template name!')
            return j

        action_name = config_template.action_provider

        try:
            action_options = json.loads(config_template.action_provider_options)
        except (ValueError, TypeError):
            logger.error('Could not load action_provider_options from config_template!')
            return j

        # let's load any secrets if necessary
        provider_options = action_provider.get_options_for_provider(action_name)
        for opt in provider_options:
            if opt['type'] == 'secret':
                opt_name = opt['name']
                pw_lookup_key = action_options[opt_name]['value']
                pw_lookup_value = aframe_utils.lookup_secret(pw_lookup_key)
                action_options[opt_name]['value'] = pw_lookup_value

        action = action_provider.get_provider_instance(action_name, action_options)

        try:
            results = action.execute_template(config_template.template.strip().replace('\r\n', '\n'))
            print results
            results_object = json.loads(results)
            print key
            print value
            d = aframe_utils.get_list_from_json(key, value, results_object, list(), 0)
            print d
            j["widget_data"] = d

        except Exception as ex:
            print str(ex)
            return j
