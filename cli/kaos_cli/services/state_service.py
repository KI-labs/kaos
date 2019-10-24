import os
import shutil
from configparser import ConfigParser, ExtendedInterpolation

from kaos_cli.constants import KAOS_STATE_DIR, DEFAULTS, CONFIG_PATH


class StateService:

    def __init__(self, config=None):
        self.config = config or ConfigParser(defaults=DEFAULTS, interpolation=ExtendedInterpolation())
        self.config.read(CONFIG_PATH)

    def set(self, section, **kwargs):
        self.config[section] = kwargs

    def get(self, section, param):
        return self.config.get(section, param)

    def has_section(self, section):
        return self.config.has_section(section)

    def remove_section(self, section):
        self.config.remove_section(section)

    @staticmethod
    def is_created(dir_build):
        return os.path.exists(dir_build)

    @staticmethod
    def create():
        shutil.rmtree(KAOS_STATE_DIR, ignore_errors=True)
        os.mkdir(KAOS_STATE_DIR)

    @staticmethod
    def delete():
        shutil.rmtree(KAOS_STATE_DIR, ignore_errors=True)

    def write(self):
        with open(CONFIG_PATH, 'w') as f:
            self.config.write(f)
