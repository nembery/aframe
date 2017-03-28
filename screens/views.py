import json
import logging

from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.template import TemplateDoesNotExist

from a_frame import settings
from input_forms.models import InputForm
from models import Screen

logger = logging.getLogger(__name__)


# Create your views here.
def index(request):
    logger.info("__ screens index __")
    screen_list = Screen.objects.all().order_by("name")
    context = {"screen_list": screen_list}
    return render(request, "screens/index.html", context)


def new(request):
    logger.info("__ screens new __")
    screens = Screen.objects.all().order_by("name")
    themes = settings.REGISTERED_APP_THEMES
    widgets = settings.SCREEN_WIDGETS
    context = {"screens": screens, "themes": themes, 'widgets': widgets}
    return render(request, "screens/new.html", context)


def delete(request, screen_id):
    logger.info("__ screens delete __")
    screen = get_object_or_404(Screen, pk=screen_id)
    screen.delete()
    return HttpResponseRedirect("/screens")


def detail(request, screen_id):
    logger.info("__ screens detail __")
    screen = get_object_or_404(Screen, pk=screen_id)
    input_forms_list = screen.input_forms.all().order_by("id")
    input_form_ids = list()
    input_forms = dict()

    for input_form in input_forms_list:
        input_form_ids.append(input_form.id)
        input_forms[input_form.id] = input_form.name

    ifi_json = json.dumps(input_form_ids)
    input_forms_json = json.dumps(input_forms)

    widgets_list = screen.screen_widgets.all().order_by("id")
    widget_ids = list()
    for widget in widgets_list:
        widget_ids.append(widget.id)

    wi_json = json.dumps(widget_ids)

    themes = settings.REGISTERED_APP_THEMES
    available_widgets = settings.SCREEN_WIDGETS

    context = {'screen': screen,
               'input_forms_json': input_forms_json,
               'input_form_ids': ifi_json,
               'widgets': widgets_list,
               'widget_ids': wi_json,
               'layout': screen.layout,
               'available_widgets': available_widgets,
               'themes': themes}

    return render(request, "screens/detail.html", context)


def create(request):
    logger.info("__ screens create __")
    required_fields = set(["name", "theme", "description", "input_forms"])
    if not required_fields.issubset(request.POST):
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    name = request.POST["name"]
    theme = request.POST["theme"]
    description = request.POST["description"]
    input_forms = request.POST["input_forms"]

    screen = Screen()
    screen.name = name
    screen.theme = theme
    screen.description = description
    screen.save()

    if input_forms == "":
        input_forms_data = []
    else:
        input_forms_data = json.loads(input_forms)

    print input_forms_data

    layout = dict()
    layout['input_forms'] = dict()
    layout['widgets'] = dict()

    xcounter = 140
    ycounter = 240
    for name in input_forms_data:
        input_form = InputForm.objects.filter(name=name)[0]

        layout['input_forms'][input_form.id] = dict()
        layout['input_forms'][input_form.id]["x"] = xcounter
        layout['input_forms'][input_form.id]["y"] = ycounter

        if xcounter <= 900:
            xcounter += 360
        else:
            ycounter += 500
            xcounter = 160

        screen.input_forms.add(input_form)

    screen.layout = json.dumps(layout)
    screen.save()
    screen_id = screen.id
    return HttpResponseRedirect("/screens/" + str(screen_id))


def edit(request):
    return HttpResponseRedirect("/screens")


def update(request):
    logger.info("__ screens update __")
    required_fields = set(["screen_id", "screen_id", "name", "description", "json"])
    if not required_fields.issubset(request.POST):
        logger.error("Did no find all required fields in request")
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    screen_id = request.POST["screen_id"]
    name = request.POST["name"]
    description = request.POST["description"]
    json_data = request.POST["json"]
    instructions = request.POST["instructions"]

    screen = get_object_or_404(Screen, pk=screen_id)

    screen.id = screen_id
    screen.name = name
    screen.description = description
    screen.instructions = instructions
    screen.json = json_data
    screen.script = screen
    screen.save()
    return HttpResponseRedirect("/screens")


def update_layout(request):
    logger.info("__ screens update_layout __")
    required_fields = set(["screen_id", "layout", "theme"])
    if not required_fields.issubset(request.POST):
        logger.error("Did no find all required fields in request")
        return render(request, "overlay_basic.html", {"message": "Layout Could not be updated!"})

    screen_id = request.POST["screen_id"]
    layout = request.POST["layout"]
    theme = request.POST["theme"]

    print layout

    screen = get_object_or_404(Screen, pk=screen_id)
    screen.layout = layout
    screen.theme = theme
    layout_obj = json.loads(layout)

    input_forms_list = screen.input_forms.all().order_by("id")

    # first let's find any input forms that have been deleted
    for inf in input_forms_list:
        found = False
        for input_form_id in layout_obj.keys():
            if str(inf.id) == str(input_form_id):
                found = True
                break

        if not found:
            print "Removing: " + str(inf.id)
            input_form = InputForm.objects.get(pk=inf.id)
            screen.input_forms.remove(input_form)

    # now let's add any news ones that have been configured
    for input_form_id in layout_obj['input_forms'].keys():
        print input_form_id
        found = False
        for inf in input_forms_list:
            if inf.id == input_form_id:
                found = True
                break

        if not found:
            input_form = InputForm.objects.get(pk=input_form_id)
            screen.input_forms.add(input_form)

    screen.save()

    return render(request, "overlay_basic.html", {"message": "Layout Updated successfully!"})


def load_widget_config(request):
    """
    Load the configuration for a given screen widget
    :param request: http request
    :return: html template
    """
    logger.info("__ screens load_widget_config __")
    required_fields = set(["widget_id", "screen_id", "widget_config_id"])
    if not required_fields.issubset(request.POST):
        logger.error("Did no find all required fields in request")
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    widget_id = request.POST["widget_id"]
    screen_id = request.POST["screen_id"]
    widget_config_id = request.POST["widget_config_id"]

    widgets = settings.SCREEN_WIDGETS
    widget_name = ""
    widget_configuration_template = ""

    found = False
    for w in widgets:

        if w["id"] == widget_id:
            widget_name = w["label"]
            widget_configuration_template = w["configuration_template"]
            logger.debug(widget_configuration_template)
            found = True
            break

    if not found:
        return render(request, "screens/widgets/overlay_error.html",
                      {"error": "Could not find widget configuration"})

    try:
        context = {"widget_id": widget_id, "widget_name": widget_name, "widget_config_id": widget_config_id}
        return render(request, "screens/widgets/%s" % widget_configuration_template, context)
    except TemplateDoesNotExist:
        return render(request, "screens/widgets/overlay_error.html",
                      {"error": "Could not load widget configuration"})


def load_widget(request):
    """
    Load the configuration for a given screen widget
    :param request: http request
    :return: html template
    """
    logger.info("__ screens load_widget_ __")
    required_fields = set(["widget_id", "widget_config_id"])
    if not required_fields.issubset(request.POST):
        logger.error("Did no find all required fields in request")
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    widget_id = request.POST["widget_id"]
    widget_config_id = request.POST["widget_config_id"]

    widgets = settings.SCREEN_WIDGETS
    widget_name = ""

    found = False
    for w in widgets:
        if w["id"] == widget_id:
            widget_name = w["label"]
            widget_template = w["render_template"]
            found = True
            break

    if not found:
        return render(request, "screens/widgets/overlay_error.html",
                      {"error": "Could not find widget configuration"})

    try:
        context = {"widget_id": widget_id, "widget_name": widget_name, "widget_config_id": widget_config_id}
        return render(request, "screens/widgets/%s" % widget_template, context)

    except TemplateDoesNotExist:
        return render(request, "screens/widgets/overlay_error.html",
                      {"error": "Could not load widget configuration"})