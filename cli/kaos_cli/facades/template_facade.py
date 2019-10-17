import json
import os
import shutil

from kaos_cli.constants import METADATA_JSON, TEMPLATE_DIR
from kaos_cli.utils.validators import validate_index, validate_names


class TemplateFacade:

    def get_template_name_by_ind(self, ind):
        templates = self.list()
        loc = validate_index(len(templates), ind, command='template')
        return templates[loc]["name"]

    def validate(self, name):
        templates = self.list()
        return validate_names([t["name"] for t in templates], name, command='template')

    @staticmethod
    def list():
        with open(os.path.join(TEMPLATE_DIR, METADATA_JSON)) as f:
            return json.load(f)

    @staticmethod
    def download(name):
        local_template_path = os.path.join(os.getcwd(), 'templates', name)
        if os.path.exists(local_template_path):
            shutil.rmtree(local_template_path)
        shutil.copytree(os.path.join(TEMPLATE_DIR, name), local_template_path)
