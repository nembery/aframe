from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from endpoints import endpoint_provider
from a_frame import settings
from models import EndpointGroup
import json


def index(request):
    provider_list = EndpointGroup.objects.all().order_by("name")
    context = {"provider_list": provider_list}
    return render(request, "endpoints/index.html", context)


def new_group(request):
    provider_list = endpoint_provider.get_endpoint_discovery_provider_list()
    context = {"provider_list": provider_list}
    return render(request, "endpoints/new_group.html", context)


def configure_group(request):
    required_fields = set(["name", "description", "provider_class"])
    if not required_fields.issubset(request.POST):
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    provider_class = request.POST["provider_class"]
    name = request.POST["name"]
    description = request.POST["description"]

    print str(provider_class)

    provider_instance = endpoint_provider.get_provider_instance(provider_class)

    provider_options = provider_instance.get_config_options()

    provider_options_json = json.dumps(provider_options)

    context = {
        "group_name": name, "group_description": description, "provider_class": provider_class,
        "provider_options": provider_options, "provider_options_json": provider_options_json
    }
    return render(request, "endpoints/configure_group.html", context)


def create_group(request):
    required_fields = set(["group_name", "group_description", "provider_class", "provider_options"])
    if not required_fields.issubset(request.POST):
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    provider_class = request.POST["provider_class"]
    name = request.POST["group_name"]
    description = request.POST["group_description"]
    provider_configuration = request.POST["provider_options"]

    print provider_configuration

    group = EndpointGroup()
    group.provider_class = provider_class
    group.name = name
    group.description = description
    group.provider_configuration = provider_configuration

    group.save()

    return HttpResponseRedirect("/endpoints/list/%s" % group.id)


def delete_group(request, group_id):
    group = get_object_or_404(EndpointGroup, pk=group_id)
    group.delete()
    return HttpResponseRedirect("/endpoints/")


def endpoint_list(request, group_id):

    group = get_object_or_404(EndpointGroup, pk=group_id)
    provider_instance = endpoint_provider.get_provider_instance_from_group(group_id)

    page_size = int(settings.DEVICE_LIST_PAGING_SIZE)
    offset = 0
    prev = -1
    next_offset = offset + page_size
    filter_name = ""
    argument = ""

    if "o" in request.GET:
        offset = int(request.GET["o"])

    if offset > 0:
        prev = offset - page_size

    if "filter" in request.GET and "argument" in request.GET:
        filter_name = request.GET["filter"]
        argument = request.GET["argument"]
        provider_instance.apply_filter(filter_name, argument)

    endpoint_array = provider_instance.get_page(offset, page_size)

    if len(endpoint_array) < page_size:
        next_offset = -1

    filters = provider_instance.available_filters()

    endpoint_queue = []
    endpoint_queue_names = []

    if "endpoint_queue" in request.session:
        endpoint_queue = request.session["endpoint_queue"]

    if "endpoint_queue_names" in request.session:
        endpoint_queue_names = request.session["endpoint_queue_names"]

    context = {"endpoint_list": endpoint_array,
               "endpoint_group": group,
               "provider": group.provider_class,
               "provider_instance": provider_instance,
               "prev": prev,
               "next": next_offset,
               "filters": filters,
               "filter": filter_name,
               "argument": argument,
               "endpoint_queue": endpoint_queue,
               "endpoint_queue_names": endpoint_queue_names
               }
    return render(request, "endpoints/list.html", context)


def endpoint_details(request, group_id, endpoint_id):

    # get the right provider instance
    provider_instance = endpoint_provider.get_provider_instance_from_group(group_id)

    endpoint = provider_instance.get_endpoint_by_id(endpoint_id)

    context = {"endpoint": endpoint, "group_id": group_id}
    return render(request, "endpoints/details.html", context)


def provider_list_json(request):
    provider_list = endpoint_provider.get_endpoint_discovery_provider_list()
    response_data = {"result": provider_list}
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def provider_filters(request, provider_name):
    provider_instance = endpoint_provider.get_provider_instance(provider_name)
    filters = provider_instance.available_filters()
    response_data = {"result": filters}
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def add_endpoints_to_queue(request):
    """
    takes a list of selected endpoints and adds them to the user session under a key named
    "endpoint_queue". Also adds another list of "endpoint_queue_names" to avoid limitations with django template
    language stuff to show already selected items in the queue

    """
    required_fields = set(["endpoints", "group_id"])
    if not required_fields.issubset(request.POST):
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    group_id = request.POST["group_id"]
    provider_instance = endpoint_provider.get_provider_instance_from_group(group_id)

    endpoint_queue = []
    endpoint_queue_names = []

    if "endpoint_queue" in request.session:
        endpoint_queue = request.session["endpoint_queue"]

    if "endpoint_queue_names" in request.session:
        endpoint_queue_names = request.session["endpoint_queue_names"]

    for e in request.POST.getlist("endpoints"):
        endpoint = provider_instance.get_endpoint_by_id(e)
        if endpoint not in endpoint_queue:
            endpoint_queue.append(endpoint)
            endpoint_queue_names.append(endpoint["name"])

    request.session["endpoint_queue"] = endpoint_queue
    request.session["endpoint_queue_names"] = endpoint_queue_names

    return HttpResponseRedirect("/endpoints/list/%s" % group_id)


def clear_endpoint_queue(request, provider):
    if "endpoint_queue" in request.session:
        request.session["endpoint_queue"] = []
    if "endpoint_queue_names" in request.session:
        request.session["endpoint_queue_names"] = []

    return HttpResponseRedirect("/endpoints/list/%s" % provider)


