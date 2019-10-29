import glob
import os
import shutil
import json
from configparser import ConfigParser, ExtendedInterpolation

from kaos_cli.constants import KAOS_STATE_DIR, CONFIG_PATH, KAOS_TF_PATH, ENVIRONMENTS


class StateService:

    def __init__(self, config=None):
        # self.config = config or ConfigParser(defaults=DEFAULTS, interpolation=ExtendedInterpolation())
        # self.config.read(CONFIG_PATH)
        # self.config.read_dict(CONFIG_PATH)
        self.data = self.read_config(CONFIG_PATH, ENVIRONMENTS)

    @staticmethod
    def read_config(path, environments):
        if os.path.exists(path):
            with open(path, 'r') as f:
                config = json.load(f)
                return config[environments]
        else:
            return []

    def set(self, section, **kwargs):
        environments = self.data
        if environments:
            for env in environments:
                env[section][kwargs] == kwargs

    def get(self, section, param):
        environments = self.data
        print("environments", environments)
        if environments:
            print("inside get")
            for env in environments:
                if env['active'] is True:
                    return env[section][param]
        return None

    def add_context(self, context_configuration):
        print("inside add context")
        environments = self.data
        environments.append(context_configuration)
        self.data = environments

    def update_context(self, current_context, context_configuration):
        print("inside update context")
        existing_environments = self.data
        environments = []
        if existing_environments:
            for env in existing_environments:
                if env['context'] != current_context and env['active'] is True:
                        env['active'] = False
                        environments.append(env)
                elif env['context'] == current_context:
                    pass
                    # do not append environment
        environments.append(context_configuration)
        self.data = environments

    def get_all_contexts(self):
        print("inside get all contexts")
        all_contexts = []
        active_context = None
        environments = self.data
        if environments:
                for env in environments:
                    all_contexts.append(env['context'])
                    if env['active'] is True:
                        active_context = env['context']
        print("active_context", active_context)
        print("all_contexts", all_contexts)
        return all_contexts, active_context

    def get_old(self, section, param):
        return self.config.get(section, param)

    def has_section_old(self, section):
        return self.config.has_section(section)

    def remove_section_old(self, section):
        self.config.remove_section(section)

    def parse_config_json(self, config_path):
        with open(config_path, 'r') as f:
            self.data = json.load(f)

    @staticmethod
    def is_created():
        return os.path.exists(KAOS_STATE_DIR)

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
    def full_delete():
        shutil.rmtree(KAOS_STATE_DIR, ignore_errors=True)

    def write(self, environments):
        with open(CONFIG_PATH, 'w'):
            data = self.data
            config = {environments: data}
            json.dumps(config)
