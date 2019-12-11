import glob
import os
import shutil
from configobj import ConfigObj

from kaos_cli.constants import KAOS_STATE_DIR, CONFIG_PATH, KAOS_TF_PATH


class StateService:

    def __init__(self, config=None):
        self.config = config or ConfigObj(CONFIG_PATH)

    def set(self, section, **kwargs):
        self.config[section] = kwargs

    def get(self, section, param):
        return self.config[section][param]

    def set_section(self, context, section, **kwargs):
        self.config[context][section] = kwargs

    def get_section(self, context, section, param):
        return self.config[context][section][param]

    def has_section(self, context, section):
        return self.config[context][section]

    def remove(self, section):
        del self.config[section]

    def remove_section(self, context, section):
        del self.config[context][section]

    @staticmethod
    def is_created(dir_build):
        return os.path.exists(dir_build)

    @staticmethod
    def create():
        shutil.rmtree(KAOS_STATE_DIR, ignore_errors=True)
        os.mkdir(KAOS_STATE_DIR)

    @staticmethod
    def list_providers():
        return [f for f in glob.glob(f'{KAOS_TF_PATH}/**/terraform.tfstate', recursive=True)]

    @staticmethod
    def provider_delete(dir_build):
        shutil.rmtree(dir_build, ignore_errors=True)

    @staticmethod
    def full_delete(dir_build):
        shutil.rmtree(dir_build, ignore_errors=True)

    def write(self):
        if not os.path.exists(KAOS_STATE_DIR):
            os.mkdir(KAOS_STATE_DIR)
        with open(CONFIG_PATH, 'wb') as f:
            self.config.write(f)
