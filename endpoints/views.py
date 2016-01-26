from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from a_frame.utils import endpoint_provider
from a_frame import settings
import json


def index(request):
    provider_list = endpoint_provider.get_endpoint_discovery_provider_list()
    context = {'provider_list': provider_list}
    return render(request, 'endpoints/index.html', context)


def endpoint_list(request, provider):
    provider_instance = endpoint_provider.get_provider_instance(provider)

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

    job_endpoints = []
    job_endpoint_names = []

    if "job_endpoints" in request.session:
        job_endpoints = request.session["job_endpoints"]

    if "job_endpoint_names" in request.session:
        job_endpoint_names = request.session["job_endpoint_names"]

    context = {"endpoint_list": endpoint_array,
               "provider": provider,
               "provider_instance": provider_instance,
               "prev": prev,
               "next": next_offset,
               "filters": filters,
               "filter": filter_name,
               "argument": argument,
               "job_endpoints": job_endpoints,
               "job_endpoint_names": job_endpoint_names
               }
    return render(request, 'endpoints/list.html', context)


def endpoint_details(request, provider, endpoint_id):
    provider_instance = endpoint_provider.get_provider_instance(provider)
    endpoint = provider_instance.get_endpoint_by_id(endpoint_id)
    print endpoint
    context = {'endpoint': endpoint, 'provider': provider}
    return render(request, 'endpoints/details.html', context)


def provider_list_json(request):
    provider_list = endpoint_provider.get_endpoint_discovery_provider_list()
    response_data = {"result": provider_list}
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def provider_filters(request, provider_name):
    provider_instance = endpoint_provider.get_provider_instance(provider_name)
    filters = provider_instance.available_filters()
    response_data = {"result": filters}
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def add_endpoints_to_job(request):
    """
    takes a list of selected endpoints and adds them to the user session under a key named
    'job_endpoints'. Also adds another list of 'job_endpoint_names' to avoid limitiations with django template
    language stuff to show already selected items in the queue

    """
    required_fields = set(['endpoints', 'endpoint_provider'])
    if not required_fields.issubset(request.POST):
        return render(request, 'error.html', {'error': "Invalid Parameters in POST"})

    endpoint_provider_name = request.POST["endpoint_provider"]

    job_endpoints = []
    job_endpoint_names = []

    if "job_endpoints" in request.session:
        job_endpoints = request.session["job_endpoints"]

    if "job_endpoint_names" in request.session:
        job_endpoint_names = request.session["job_endpoint_names"]

    provider_instance = endpoint_provider.get_provider_instance(endpoint_provider_name)
    for e in request.POST.getlist("endpoints"):
        endpoint = provider_instance.get_endpoint_by_id(e)
        if endpoint not in job_endpoints:
            job_endpoints.append(endpoint)
            job_endpoint_names.append(endpoint["name"])

    request.session["job_endpoints"] = job_endpoints
    request.session["job_endpoint_names"] = job_endpoint_names

    return HttpResponseRedirect('/endpoints/list/%s' % endpoint_provider_name)


def clear_job_endpoints(request, provider):
    if "job_endpoints" in request.session:
        request.session["job_endpoints"] = []
    if "job_endpoint_names" in request.session:
        request.session["job_endpoint_names"] = []

    return HttpResponseRedirect('/endpoints/list/%s' % provider)


