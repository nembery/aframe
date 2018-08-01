import json
import logging
import os


from django.apps import AppConfig
import shutil

logger = logging.getLogger(__name__)


class InputFormAppConfig(AppConfig):
    name = 'input_forms'
    verbose_name = "input_forms"

    def ready(self):
        from common.lib import aframe_utils

        common_lib_dir = os.path.dirname(os.path.abspath(__file__))
        imports_dir = os.path.abspath(os.path.join(common_lib_dir, '../conf/imports/forms'))
        output_parsers_dir = os.path.abspath(os.path.join(common_lib_dir, '../conf/imports/output_parsers'))

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

                        aframe_utils.import_form(json_data)

        if os.path.exists(output_parsers_dir):
            for f in os.listdir(output_parsers_dir):
                if f.endswith(".html"):
                    fp = os.path.join(output_parsers_dir, f)
                    # dest_path = os.path.join('templates/input_forms/output_parsers', f)
                    dest_path = os.path.join(common_lib_dir, 'templates/input_forms/output_parsers')
                    dest_file = os.path.join(dest_path, f)
                    if not os.path.exists(dest_file):
                        logger.debug("Found an output parser to import !")
                        shutil.copy(fp, dest_file)
