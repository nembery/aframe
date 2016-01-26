from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse

import json

from tools.models import ConfigTemplate
from tools.models import ConfigTemplateForm

from tools.models import Script
from tools.models import ScriptForm

from a_frame.utils import action_provider
from a_frame import settings


def index(request):
    template_list = ConfigTemplate.objects.all().order_by('modified')
    script_list = Script.objects.all().order_by('modified')
    context = {'template_list': template_list, 'script_list': script_list}
    return render(request, 'configTemplates/index.html', context)


def choose_action(request):

    action_providers = action_provider.get_action_provider_select()

    context = {'action_providers': action_providers}
    return render(request, 'configTemplates/choose_action.html', context)


def configure_action(request):
    """
    FIXME - add some validation here
    :param request:
    :return:
    """
    provider_name = request.POST["action_provider"]

    action_options = action_provider.get_options_for_provider(provider_name)

    if action_options == "":
        context = {'error': 'action provider not found'}
        return render(request, 'error.html', context)

    context = {'action_options': action_options, 'action_provider': provider_name}
    return render(request, 'configTemplates/configure_action.html', context)


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
            context = {'error': 'Required option not found in request!'}
            return render(request, 'error.html', context)

    print "Setting configured options to the session %s" % configured_options
    request.session["new_template_action_options"] = configured_options
    context = {'options': configured_options, 'action_provider': action_provider_name}
    return render(request, 'configTemplates/define_template.html', context)


def new_template(request):

    action_providers = action_provider.get_action_provider_select()

    template_form = ConfigTemplateForm()
    template_form.fields["action_provider"].choices = action_providers
    context = {'template_form': template_form, 'action_providers': action_providers}
    return render(request, 'configTemplates/new.html', context)


def get_options_for_action(request):
    action_name = request.POST["action_name"]
    print action_name
    for a in settings.ACTION_PROVIDERS:
        print a
        if a["name"] == action_name:
            return HttpResponse(json.dumps(a), content_type="application/json")


def edit(request, template_id):
    template = get_object_or_404(ConfigTemplate, pk=template_id)

    template_form = ConfigTemplateForm(instance=template)
    context = {'template_form': template_form, 'template': template}
    return render(request, 'configTemplates/edit.html', context)


def update(request):
    try:
        if "id" in request.POST:
            template_id = request.POST['id']
            template = get_object_or_404(ConfigTemplate, pk=template_id)
            template.name = request.POST['name']
            template.description = request.POST['description']
            template.template = request.POST['template']
            template.action_provider_options = request.POST["action_provider_options"]
            template.save()
            return HttpResponseRedirect('/tools')
        else:
            return render(request, 'error.html', {
                'error_message': "Invalid data in POST"
            })

    except KeyError:
        return render(request, 'error.html', {
            'error_message': "Invalid data in POST"
        })


def create(request):
    required_fields = set(['name', 'description', 'template', 'type'])
    if not required_fields.issubset(request.POST):
        return render(request, 'error.html', {'error': "Invalid Parameters in POST"})

    template = ConfigTemplate()
    template.name = request.POST["name"]
    template.description = request.POST["description"]
    template.action_provider = request.POST["action_provider"]
    template.template = request.POST["template"]
    template.type = request.POST["type"]

    if "new_template_action_options" not in request.session:
        return render(request, 'error.html', {
            'error_message': "Invalid session data!"
        })

    configured_action_options = request.session["new_template_action_options"]
    template.action_provider_options = json.dumps(configured_action_options)

    print "Saving form"
    template.save()
    return HttpResponseRedirect('/input_forms/view_from_template/%s' % template.id)


def detail(request, template_id):
    template = get_object_or_404(ConfigTemplate, pk=template_id)
    return render(request, 'configTemplates/details.html', {'template': template})


def delete(request, template_id):
    template = get_object_or_404(ConfigTemplate, pk=template_id)
    template.delete()
    return HttpResponseRedirect('/tools')


def error(request):
    context = {'error': "Unknown Error"}
    return render(request, 'error.html', context)


def new_script(request):
    script_form = ScriptForm()
    context = {'script_form': script_form}
    return render(request, 'scripts/new.html', context)


def create_script(request):
    required_fields = set(['name', 'description', 'script'])
    if not required_fields.issubset(request.POST):
        return render(request, 'error.html', {
            'error': "Form isn't valid!"
        })

    # clean up crlf
    script_content = request.POST["script"]
    request.POST["script"] = script_content.replace("\r", "")

    script_form = ScriptForm(request.POST, request.FILES)
    if script_form.is_valid():
        print "Saving form"
        script_form.save()
        return HttpResponseRedirect('/tools')
    else:
        context = {'error': "Form isn't valid!"}
        return render(request, 'error.html', context)


def view_script(request, script_id):
    script = get_object_or_404(Script, pk=script_id)
    return render(request, 'scripts/details.html', {'script': script})


def edit_script(request, script_id):
    script = get_object_or_404(Script, pk=script_id)
    script_form = ScriptForm(instance=script)
    context = {'script_form': script_form, 'script': script}
    return render(request, 'scripts/edit.html', context)


def update_script(request):
    required_fields = set(['id', 'name', 'description', 'script'])
    if not required_fields.issubset(request.POST):
        return render(request, 'scripts/error.html', {
            'error_message': "Invalid data in POST"
        })
    try:
        if "id" in request.POST:
            script_id = request.POST['id']
            script = get_object_or_404(Script, pk=script_id)
            script.name = request.POST['name']
            script.description = request.POST['description']
            script.script = request.POST['script'].replace("\r", "")
            script.save()
            return HttpResponseRedirect('/tools')
        else:
            return render(request, 'scripts/error.html', {
                'error_message': "Invalid data in POST"
            })

    except Exception as e:
        print str(e)
        return render(request, 'scripts/error.html', {
            'error_message': 'Could not update script!'
        })


def delete_script(request, script_id):
    script = get_object_or_404(Script, pk=script_id)
    script.delete()
    return HttpResponseRedirect('/tools')
