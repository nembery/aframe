import json
import logging
import os


from django.apps import AppConfig

logger = logging.getLogger(__name__)


class InputFormAppConfig(AppConfig):
    name = 'input_forms'
    verbose_name = "input_forms"

    def ready(self):
        from common.lib import aframe_utils

        common_lib_dir = os.path.dirname(os.path.abspath(__file__))
        imports_dir = os.path.abspath(os.path.join(common_lib_dir, '../conf/imports/forms'))

        if os.path.exists(imports_dir):
            for f in os.listdir(imports_dir):
                if f.endswith(".json"):
                    logger.debug("Found a json file import!")
                    fp = os.path.join(imports_dir, f)
                    with open(fp, 'r') as fo:
                        json_string = fo.read()
                        try:
                            json_data = json.loads(json_string)
                        except ValueError:
                            logger.error('Could not load json file in import directory')
                            continue

                        # template_options = json_data["template"]
                        # form_options = json_data["form"]
                        #
                        # if not ConfigTemplate.objects.filter(name=template_options['name']).exists():
                        #     template = ConfigTemplate()
                        #     template.name = template_options["name"]
                        #     template.description = template_options["description"]
                        #     template.action_provider = template_options["action_provider"]
                        #     template.action_provider_options = template_options["action_provider_options"]
                        #     template.type = template_options["type"]
                        #     template.template = unquote(template_options["template"])
                        #     logger.info("Imported template: %s" % template.name)
                        #     template.save()
                        #
                        # if not InputForm.objects.filter(name=form_options['name']).exists():
                        #     input_form = InputForm()
                        #     input_form.name = form_options["name"]
                        #     input_form.description = form_options["description"]
                        #     input_form.instructions = form_options["instructions"]
                        #     input_form.json = unquote(form_options["json"])
                        #     input_form.script = template
                        #
                        #     logger.info("Import input form: %s" % input_form.name)
                        #     input_form.save()

                        aframe_utils.import_forms(json_data)
