import json
import logging
import os
from shutil import copyfile
from urllib import unquote

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class ScreensAppConfig(AppConfig):
    name = 'screens'
    verbose_name = 'screens'

    def ready(self):

        print 'Checking for imported screens'
        from screens.models import Screen
        from screens.models import ScreenWidgetConfig

        from common.lib import aframe_utils

        common_lib_dir = os.path.dirname(os.path.abspath(__file__))
        imports_dir = os.path.abspath(os.path.join(common_lib_dir, '../conf/imports/themes'))
        screens_dir = os.path.abspath(os.path.join(common_lib_dir, '../conf/imports/screens'))

        themes_dir = os.path.abspath(os.path.join(common_lib_dir, '../screens/templates/themes'))

        if os.path.exists(imports_dir):
            for f in os.listdir(imports_dir):
                if f.endswith(".html") or f.endswith('.css'):
                    logger.debug("Found a theme file to import!")
                    fs = os.path.join(imports_dir, f)
                    fd = os.path.join(themes_dir, f)
                    if not os.path.exists(fd):
                        copyfile(fs, fd)
                    else:
                        logger.info('theme already exists in themes dir')

        if os.path.exists(screens_dir):
            for f in os.listdir(screens_dir):
                print 'checking to import screen %s' % f
                if f.endswith(".json"):
                    print 'Importing json file'
                    logger.debug("Found a screen to import!")
                    s = os.path.join(screens_dir, f)
                    with open(s, 'r') as fo:
                        json_string = fo.read()
                        try:
                            json_data = json.loads(json_string)
                        except ValueError:
                            print 'Could not load json from screen file!'
                            logger.error('Could not load json file in import directory')
                            continue

                    try:
                        # screen export creates a dict with two keys 'screen' and 'input_forms'
                        # 'screen' key holds metadata about the screen
                        screen_data = json_data['screen']

                        if Screen.objects.filter(name=screen_data['name']).exists():
                            print 'Skipping existing screen %s' % screen_data['name']
                            continue

                        # 'input_forms' holds all the referenced input_forms in that screen
                        # each of these is 'exported' in whole, serialized, and kept here
                        form_data = json_data['input_forms']

                        # we will also export any global widget data that is found on widgets in the screen
                        widget_data = json_data['widgets']

                        for w in widget_data:
                            if not ScreenWidgetConfig.filter(widget_type=w).exists():
                                widget_config = ScreenWidgetConfig()

                                widget_config.widget_type = w
                                widget_config.data = unquote(widget_data[w])
                                widget_config.save()

                        # we need to update the layout with new input form ids after we import those
                        layout = json.loads(screen_data['layout'])

                        # create new layout object
                        new_layout = dict()
                        # we can just copy the widgets right in
                        new_layout['widgets'] = layout['widgets']
                        new_layout['input_forms'] = dict()

                        # iterate over all exported input forms
                        for sid in form_data.keys():
                            # let's get the entire form that was previously exported in full
                            screen_form = form_data[sid]
                            # convert back from json
                            screen_form_data = json.loads(screen_form)
                            # do the import here and get it's updated ID
                            new_id = aframe_utils.import_form(screen_form_data)
                            # these should absolutely already exist in the layout
                            if sid in layout['input_forms'].keys():
                                print 'updating layout %s to %s' % (sid, new_id)
                                new_layout['input_forms'][new_id] = layout['input_forms'][sid]

                        if not Screen.objects.filter(name=screen_data['name']).exists():
                            screen = Screen()
                            screen.name = screen_data['name']
                            screen.description = screen_data['description']
                            screen.theme = screen_data['theme']
                            screen.layout = json.dumps(new_layout)
                            screen.save()
                        else:
                            print 'Screen already exists!'

                    except KeyError as ke:
                        print 'some keyerror'
                        print ke
                        logger.error('Could not import screen!')
                        continue
