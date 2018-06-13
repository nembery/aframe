import json
import logging
from urllib import quote

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, HttpResponse
from django.template import TemplateDoesNotExist
from django.db.models import Q

from a_frame import settings
from common.lib import aframe_utils
from input_forms.models import InputForm
from models import Screen
from models import ScreenWidgetConfig
from models import ScreenWidgetData

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
    # themes = settings.REGISTERED_APP_THEMES
    themes = aframe_utils.get_screen_themes()
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
    # input_forms_list = screen.input_forms.all().order_by("id")
    input_form_ids = list()
    input_forms = dict()

    # for input_form in input_forms_list:
    #    input_form_ids.append(input_form.id)
    #    input_forms[input_form.id] = input_form.name

    layout_obj = json.loads(screen.layout)
    print layout_obj['input_forms']
    for inf in layout_obj.get('input_forms', []):
        print 'input form tuype is'
        print type(inf)
        if InputForm.objects.filter(pk=inf).exists():
            input_form = InputForm.objects.get(pk=inf)
            input_form_ids.append(int(inf))
            input_forms[inf] = input_form.name
        else:
            print 'UNKNOWN INPUTFORM ID %s' % inf

    print 'theme is %s' % screen.theme

    ifi_json = json.dumps(input_form_ids)
    input_forms_json = json.dumps(input_forms)

    widgets_list = screen.screen_widgets.all().order_by("id")
    widget_ids = list()
    for widget in widgets_list:
        widget_ids.append(widget.id)

    wi_json = json.dumps(widget_ids)

    # themes = settings.REGISTERED_APP_THEMES
    themes = aframe_utils.get_screen_themes()
    all_widgets = settings.SCREEN_WIDGETS

    # only load non-transient widgets
    available_widgets = list()
    for aw in all_widgets:
        transient = aw.get("transient", False)
        if not transient:
            available_widgets.append(aw)

    available_widgets_json = json.dumps(available_widgets)

    context = {'screen': screen,
               'input_forms_json': input_forms_json,
               'input_form_ids': ifi_json,
               'widgets': widgets_list,
               'widget_ids': wi_json,
               'layout': screen.layout,
               'available_widgets': available_widgets,
               'available_widgets_json': available_widgets_json,
               'themes': themes}

    return render(request, "screens/detail.html", context)


def create(request):
    logger.info("__ screens create __")
    required_fields = set(["name", "theme", "description", "input_forms", "screen_widgets"])
    if not required_fields.issubset(request.POST):
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    name = request.POST["name"]
    theme = request.POST["theme"]
    description = request.POST["description"]
    input_forms = request.POST["input_forms"]
    widgets = request.POST['screen_widgets']

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

    if widgets == "":
        widgets_data = []
    else:
        widgets_data = json.loads(widgets)

    print widgets

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

    indx = 0
    for w in widgets_data:
        widget_layout = dict()
        widget_layout["x"] = xcounter
        widget_layout["y"] = ycounter

        layout['widgets'][indx] = dict()
        layout['widgets'][indx]["layout"] = widget_layout
        layout['widgets'][indx]["widget_id"] = w
        layout['widgets'][indx]["widget_config"] = dict()
        if xcounter <= 900:
            xcounter += 360
        else:
            ycounter += 500
            xcounter = 160

        indx += 1

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
    print theme

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


def export_screen(request, screen_id):
    logger.info("__ screens export __")

    screen = get_object_or_404(Screen, pk=screen_id)
    layout = screen.layout
    layout_obj = json.loads(layout)

    exported_data = dict()
    exported_data['input_forms'] = dict()
    exported_data['widgets'] = dict()

    for input_form_id in layout_obj['input_forms'].keys():
        input_form_json = aframe_utils.export_input_form(input_form_id)
        exported_data['input_forms'][input_form_id] = input_form_json

    for widget_key in layout_obj['widgets']:
        widget_id = layout_obj['widgets'][widget_key].get('widget_id', None)
        if widget_id is None:
            continue
        if ScreenWidgetConfig.objects.filter(widget_type=widget_id).exists():
            widget_config = ScreenWidgetConfig.objects.get(widget_type=widget_id)
            # context.update
            print widget_config.data
            exported_data['widgets'][widget_id] = quote(widget_config.data)

    exported_data['screen'] = dict()
    exported_data['screen']['name'] = screen.name
    exported_data['screen']['description'] = screen.description
    exported_data['screen']['theme'] = screen.theme
    exported_data['screen']['layout'] = screen.layout

    exported_json = json.dumps(exported_data)
    response = HttpResponse(exported_json, content_type="application/json")
    response['Content-Disposition'] = 'attachment; filename=' + 'aframe-' + str(screen.name) + '.json'

    return response


def load_widget_config(request):
    """
    Load the configuration for a given screen widget
    :param request: http request
    :return: html template
    """
    logger.info("__ screens load_widget_config __")
    required_fields = set(["widget_id", "widget_layout_id"])
    if not required_fields.issubset(request.POST):
        logger.error("Did no find all required fields in request")
        return render(request, "overlay_basic.html", {"message": "Invalid Parameters in POST"})

    widget_id = request.POST["widget_id"]
    widget_layout_id = request.POST["widget_layout_id"]

    widgets = settings.SCREEN_WIDGETS
    widget_name = ""
    widget_configuration_template = ""
    widget_consumes_input_form = ""

    found = False
    for w in widgets:

        if w["id"] == widget_id:
            widget_name = w["label"]
            widget_configuration_template = w["configuration_template"]
            if "consumes_input_form" in w:
                widget_consumes_input_form = w["consumes_input_form"]

            logger.debug(widget_configuration_template)
            found = True
            break

    if not found:
        return render(request, "screens/widgets/overlay_error.html",
                      {"error": "Could not find widget configuration"})

    context = {"widget_id": widget_id, "widget_name": widget_name, "widget_layout_id": widget_layout_id}

    # grab the widget global configuration if it exists and set on the context
    # FIXME - widget_type and widget_id are used interchangeably, this should just be widget_id basically everywhere
    if ScreenWidgetConfig.objects.filter(widget_type=widget_id).exists():
        print "FOUND WIDGET CONFIG"
        widget_config = ScreenWidgetConfig.objects.get(widget_type=widget_id)
        # context.update
        print widget_config.data
        context.update({"widget_global_config": widget_config.data})

    if widget_consumes_input_form != "":
        # this widget will consume the output of a configured automation!
        try:
            input_form = InputForm.objects.get(name=widget_consumes_input_form)

            logger.debug(input_form.json)
            json_object = json.loads(input_form.json)
            for jo in json_object:
                if "widget" not in jo:
                    jo["widget"] = "text_input"

            config_template = input_form.script
            action_options = json.loads(config_template.action_provider_options)

            input_form_context = {"input_form": input_form, "json_object": json_object,
                                  "action_options": action_options, "consumes_input_form": widget_consumes_input_form}

            context.update(input_form_context)

        except ObjectDoesNotExist:
            logger.error("Configured automation for widget does not exist!")

    try:
        return render(request, "screens/widgets/%s" % widget_configuration_template, context)
    except TemplateDoesNotExist:
        return render(request, "screens/widgets/overlay_error.html",
                      {"error": "Could not load widget configuration"})


def load_widget(request):
    """
    Load the configuration for a given screen widget

    Widgets can provide any functionality to the screen
    widgets can store data in 3 different places:
        Global widget configuration is stored in the ScreenWidgetConfig db table
        Global widget data is stored in the ScreenWidgetData db table
        Per Screen / Per Widget instance data is stored in the layout object on the screen itself

        For example, you may configure a graph widget globally to point to a specific automation for data
        then each graph can load specific parameters from the global widget data db table to be shared among screens
        then finally, the specific time slice can be stored in the layout data on the screen
    :param request: http request
    :return: html template
    """
    logger.info("__ screens load_widget_ __")
    required_fields = set(["widget_id"])
    if not required_fields.issubset(request.POST):
        logger.error("Did not find all required fields in request")
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    widget_id = request.POST["widget_id"]

    # widget_layout_id is an identifier used to id the specific widget config stored
    # in the layout object of this screen. This is a per-screen / per-widget id
    # widgets defined as transient do not have a widget_layout_id
    widget_layout_id = request.POST["widget_layout_id"]

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
                      {"error": "Could not find widget"})

    try:
        context = {"widget_id": widget_id,
                   "widget_name": widget_name,
                   "widget_layout_id": widget_layout_id,
                   "widget_global_config": {}
                   }

        # grab the widget global configuration if it exists and set on the context
        # FIXME - widget_type and widget_id are used interchangeably, this should just be widget_id basically everywhere
        if ScreenWidgetConfig.objects.filter(widget_type=widget_id).exists():
            print "FOUND WIDGET CONFIG"
            widget_config = ScreenWidgetConfig.objects.get(widget_type=widget_id)
            # context.update
            print widget_config.data
            context.update({"widget_global_config": widget_config.data})

        if "consumes_automation" in w:

            post_vars = dict()
            for v in request.POST:
                post_vars[v] = request.POST[v]

            post_vars["template_name"] = w["consumes_automation"]
            automation_results = aframe_utils.execute_template(post_vars)

            context.update({"automation_results": automation_results})
            try:
                # attempt to load results for the user! not every automation will return json though, so we can't
                # count on it!
                results_object = json.loads(automation_results['output'])
                context.update({"automation_output": results_object})
            except ValueError:
                print "Could not parse JSON output from automation!"
                pass

        return render(request, "screens/widgets/%s" % widget_template, context)

    except TemplateDoesNotExist:
        return render(request, "screens/widgets/overlay_error.html",
                      {"error": "Could not load widget configuration"})


#
#   CRUD data for per-widget_type data. This is data that can be only loaded by a particular widget_type
#
def create_widget_data(request):
    logger.info("__ screens create_widget_data __")
    required_fields = set(["name", "widget_type", "data"])
    if not required_fields.issubset(request.POST):
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    name = request.POST["name"]
    widget_type = request.POST["widget_type"]
    data = request.POST["data"]

    results = dict()

    if ScreenWidgetData.objects.filter(name=name).exists():
        results['status'] = False
        results['message'] = 'Screen Widget Data already exists with this name!'
        return HttpResponse(json.dumps(results), content_type="application/json")

    widget_data = ScreenWidgetData()
    widget_data.name = name
    widget_data.widget_type = widget_type
    widget_data.data = data

    widget_data.save()

    results['status'] = True
    results['message'] = 'widget data saved'

    return HttpResponse(json.dumps(results), content_type="application/json")


def update_widget_data(request):
    logger.info("__ screens update_widget_data __")
    required_fields = set(["name", "widget_type", "data"])
    if not required_fields.issubset(request.POST):
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    name = request.POST["name"]
    widget_type = request.POST["widget_type"]
    data = request.POST["data"]

    results = dict()

    if not ScreenWidgetData.objects.filter(name=name).exists():
        results['status'] = False
        results['message'] = 'Screen Widget Data does not exist!'
        return HttpResponse(json.dumps(results), content_type="application/json")

    widget_data = ScreenWidgetData.objects.get(name=name, widget_type=widget_type)
    widget_data.data = data

    widget_data.save()

    results['status'] = True
    results['message'] = 'widget data updated'

    return HttpResponse(json.dumps(results), content_type="application/json")


def get_widget_data(request):
    logger.info("__ screens get_widget_data __")
    required_fields = set(["name", "widget_type"])
    if not required_fields.issubset(request.POST):
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    name = request.POST["name"]
    widget_type = request.POST["widget_type"]

    results = dict()

    if ScreenWidgetData.objects.filter(name=name, widget_type=widget_type).exists():
        widget_data = ScreenWidgetData.objects.get(name=name, widget_type=widget_type)
        results['status'] = True
        results['data'] = widget_data.data
        results['message'] = 'found widget data'

    else:
        results['status'] = False
        results['message'] = 'widget data not found!'

    return HttpResponse(json.dumps(results), content_type="application/json")


def delete_widget_data(request):
    logger.info("__ screens delete_widget_data __")
    required_fields = set(["name", "widget_type"])
    if not required_fields.issubset(request.POST):
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    name = request.POST["name"]
    widget_type = request.POST["widget_type"]

    results = dict()

    if ScreenWidgetData.objects.filter(name=name, widget_type=widget_type).exists():
        widget_data = ScreenWidgetData.objects.get(name=name, widget_type=widget_type)
        widget_data.delete()
        results['status'] = True
        results['message'] = 'deleted widget data'

    else:
        results['status'] = True
        results['message'] = 'widget data already gone!'

    return HttpResponse(json.dumps(results), content_type="application/json")


def list_widget_data(request):
    logger.info("__ screens list_widget_data __")
    required_fields = set(["widget_type"])
    if not required_fields.issubset(request.POST):
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    widget_type = request.POST["widget_type"]
    results = dict()

    widget_data_list = ScreenWidgetData.objects.filter(widget_type=widget_type)

    wd_list = list()
    for wd in widget_data_list:
        wdd = dict()
        wdd['widget_type'] = widget_type
        wdd['name'] = wd.name
        wd_list.append(wdd)

    wdj = json.dumps(wd_list)
    results['status'] = True
    results['list'] = wdj

    return HttpResponse(json.dumps(results), content_type="application/json")


#
#   CRUD methods for global widget configuration, i.e. things that can be applied to widgets of a certain type
#   globally
#   
def save_widget_config(request):
    logger.info("__ screens save_widget_config __")
    required_fields = set(["widget_type", "data"])
    if not required_fields.issubset(request.POST):
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    widget_type = request.POST["widget_type"]
    data = request.POST["data"]

    results = dict()

    if ScreenWidgetConfig.objects.filter(widget_type=widget_type).exists():
        widget_config = ScreenWidgetConfig.objects.get(widget_type=widget_type)
    else:
        widget_config = ScreenWidgetConfig()

    widget_config.widget_type = widget_type
    widget_config.data = data

    widget_config.save()

    results['status'] = True
    results['message'] = 'widget config saved'

    return HttpResponse(json.dumps(results), content_type="application/json")


def get_widget_config(request):
    logger.info("__ screens get_widget_config __")
    required_fields = set(["widget_type"])
    if not required_fields.issubset(request.POST):
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    widget_type = request.POST["widget_type"]

    results = dict()

    if ScreenWidgetConfig.objects.filter(widget_type=widget_type).exists():
        widget_config = ScreenWidgetConfig.objects.get(widget_type=widget_type)
        results['status'] = True
        results['data'] = widget_config.data
        results['message'] = 'found widget config'

    else:
        results['status'] = False
        results['message'] = 'widget config not found!'

    return HttpResponse(json.dumps(results), content_type="application/json")


def delete_widget_config(request):
    logger.info("__ screens delete_widget_config __")
    required_fields = set(["widget_type"])
    if not required_fields.issubset(request.POST):
        return render(request, "error.html", {"error": "Invalid Parameters in POST"})

    widget_type = request.POST["widget_type"]

    results = dict()

    if ScreenWidgetConfig.objects.filter(widget_type=widget_type).exists():
        widget_config = ScreenWidgetConfig.objects.get(widget_type=widget_type)
        widget_config.delete()
        results['status'] = True
        results['message'] = 'deleted widget config'

    else:
        results['status'] = True
        results['message'] = 'widget config already gone!'

    return HttpResponse(json.dumps(results), content_type="application/json")


def search(request):
    """
    used for UI autocomplete searches. Only used on the endpoint details page. 
    :param request:
    :return: dict containing label and value keys
    """
    logger.info("__ screens search __")

    term = request.GET["term"]
    screen_list = Screen.objects.filter(Q(name__contains=term) | Q(description__contains=term))
    results = []
    for screen in screen_list:
        r = dict()
        r["value"] = screen.id
        r["label"] = screen.name + " " + screen.description
        results.append(r)

    return HttpResponse(json.dumps(results), content_type="application/json")
