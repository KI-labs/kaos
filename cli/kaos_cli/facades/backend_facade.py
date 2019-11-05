import json
import os
import shutil
import uuid
from distutils.dir_util import copy_tree

import requests
from kaos_cli.constants import DOCKER, MINIKUBE, PROVIDER_DICT, AWS, BACKEND, INFRASTRUCTURE, GCP, LOCAL_CONFIG_DICT, \
    KAOS_TF_PATH, CONTEXTS, ACTIVE, BACKEND_CACHE
from kaos_cli.exceptions.exceptions import HostnameError
from kaos_cli.services.state_service import StateService
from kaos_cli.services.terraform_service import TerraformService
from kaos_cli.utils.environment import check_environment
from kaos_cli.utils.helpers import build_dir
from kaos_cli.utils.validators import validate_build_dir, validate_cache, validate_index


def is_cloud_provider(cloud):
    return cloud not in (DOCKER, MINIKUBE)


class BackendFacade:
    """
    This class should handle all backend related configuration and settings.
    """

    def __init__(self, state_service: StateService, terraform_service: TerraformService):
        self.state_service = state_service
        self.tf_service = terraform_service

    @property
    def url(self):
        return self.state_service.get(BACKEND, 'url')

    @property
    def user(self):
        return self.state_service.get(BACKEND, 'user')

    @property
    def token(self):
        return self.state_service.get(BACKEND, 'token')

    @property
    def kubeconfig(self):
        return self.state_service.get(INFRASTRUCTURE, 'kubeconfig')

    def init(self, url, token):
        if not self.state_service.is_created():
            self.state_service.create()
        self.state_service.set(BACKEND, url=url, token=token)

        self.state_service.write()

    def list(self):
        try:
            contexts = self.state_service.get(CONTEXTS, 'environments')
            print("contexts", contexts)
            print("contexts_type", type(contexts))
            # list_contexts = contexts.split(',')
            contexts_info = self.jsonify_context_list(contexts)
            return contexts_info

        except KeyError:
            return None

    def set(self, current_context):
        pass

    @staticmethod
    def get_context_info(context):
        try:
            cloud, env = context.split('_')
        except ValueError:
            cloud = context
            env = None
        env = "local" if not env else env
        info = {
            "context": context,
            "provider": cloud,
            "env": env
        }
        return info

    def jsonify_context_list(self, contexts):
        contexts_info = []
        if isinstance(contexts, list):
            for context in contexts:
                contexts_info.append(self.get_context_info(context))
        elif isinstance(contexts, str):
            contexts_info.append(self.get_context_info(contexts))
        return contexts_info

    @staticmethod
    def set_context_by_ind(ind):
        print("in set context")
        data = validate_cache(BACKEND_CACHE, command='build')
        print("data", data)
        loc = validate_index(len(data['ind']), ind, command='build')
        print("loc", loc)
        return data['name'][loc]

    @staticmethod
    def _set_build_dir(provider, env):
        dir_build = os.path.join(KAOS_TF_PATH,
                                 f"{provider}/{env}" if provider not in [DOCKER, MINIKUBE] else f"{provider}")
        return dir_build

    def build(self, provider, env, local_backend=False, verbose=False):
        dir_build = self._set_build_dir(provider, env)
        build_dir(dir_build)
        extra_vars = self._get_vars(provider, dir_build)
        self.tf_service.cd_dir(dir_build)

        self.tf_service.set_verbose(verbose)
        directory = self._tf_init(provider, env, local_backend, destroying=False)
        self.tf_service.plan(directory, extra_vars)
        self.tf_service.apply(directory, extra_vars)
        self.tf_service.execute()

        url, kubeconfig = self._parse_config(dir_build)

        current_context = provider if provider in [DOCKER, MINIKUBE] else provider + '_' + env

        self._set_context_list(current_context)
        self._set_active_context(current_context)
        self.state_service.set(current_context)

        try:
            self.state_service.set_section(current_context, BACKEND, url=url, token=uuid.uuid4())
            self.state_service.set_section(current_context, INFRASTRUCTURE, kubeconfig=kubeconfig)
        except KeyError:
            pass
        self.state_service.write()

    def destroy(self, provider, env, verbose=False):
        dir_build = self._set_build_dir(provider, env)
        validate_build_dir(dir_build)

        extra_vars = self._get_vars(provider, dir_build)
        self.tf_service.cd_dir(dir_build)

        self.tf_service.set_verbose(verbose)
        directory = self._tf_init(provider, env, local_backend=False, destroying=True)
        current_context = provider if provider in [DOCKER, MINIKUBE] else provider + '_' + env
        self._delete_resources(current_context)
        self._unset_context_list(current_context)
        self._remove_section(current_context)
        self._deactivate_context()
        self.tf_service.destroy(directory, extra_vars)
        self.tf_service.execute()
        self._remove_build_files(dir_build)

    def is_created(self):
        return self.state_service.is_created()

    def _remove_build_files(self, dir_build):
        """
        Function to remove backend directory
        """
        self.state_service.provider_delete(dir_build)
        if not self.state_service.list_providers():
            self.state_service.full_delete()

    def _delete_resources(self, context):
        if self.state_service.has_section(context, BACKEND):
            requests.delete(f"{self.url}/internal/resources")

    def _tf_init(self, provider, env, local_backend, destroying=False):
        directory = PROVIDER_DICT.get(provider)
        check_environment(provider)
        if is_cloud_provider(provider):
            provider_directory = f"{directory}/{env}"
            directory = f"{directory}/__working_{env}"
            if not destroying or not os.path.isdir(directory):
                copy_tree(provider_directory, directory)
            if local_backend:
                shutil.copy(LOCAL_CONFIG_DICT.get(provider), directory)

            # simply always create the workspace
            self.tf_service.init(directory)
            self.tf_service.new_workspace(directory, env)
            self.tf_service.select_workspace(directory, env)

        else:
            self.tf_service.init(directory)
        return directory

    def _set_context_list(self, current_context):
        try:
            available_contexts = self.state_service.get(CONTEXTS, 'environments')
        except KeyError:
            available_contexts = ''
        updated_contexts = available_contexts + current_context if not available_contexts else \
            available_contexts + ',' + current_context
        self.state_service.set(CONTEXTS, environments=updated_contexts)

    def _unset_context_list(self, current_context):
        available_contexts = self.state_service.get(CONTEXTS, 'environments')
        context_list = available_contexts.split(',')
        if len(context_list) <= 1:
            updated_context_list = []
        else:
            try:
                context_list.remove(current_context)
            except ValueError:
                updated_context_list = context_list
        updated_contexts = ','.join(updated_context_list)
        self.state_service.set(CONTEXTS, environments=updated_contexts)

    def _set_active_context(self, current_context):
        self.state_service.set(ACTIVE, environment=current_context)

    def _remove_section(self, current_context):
        empty_section = {}
        self.state_service.set(current_context, empty_section)

    def _deactivate_context(self):
        self.state_service.set(ACTIVE, environment=None)

    @staticmethod
    def cache(builds):
        with open(BACKEND_CACHE, 'w') as fp:
            json.dump(builds, fp)

    @staticmethod
    def _parse_config(dir_build):
        """
        Basic function to extract endpoint from deployed backend service
        """
        config_json_path = os.path.join(dir_build, 'config.json')
        with open(config_json_path) as f:
            raw_config = json.load(f)

        domain_value = raw_config["backend_domain"][0]
        hostname = domain_value.get("hostname")
        ip = domain_value.get("ip")
        domain = hostname or ip

        if not domain:
            raise HostnameError("Hostname not present")

        port = int(raw_config["backend_port"])
        path = raw_config["backend_path"]

        url = f"http://{domain}:{port}{path}"
        kubeconfig = raw_config["kubeconfig"]
        return url, kubeconfig

    @staticmethod
    def _get_vars(provider, dir_build):
        extra_vars = f"--var config_dir={dir_build} "

        if provider == AWS:
            KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
            SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
            REGION = os.getenv("AWS_DEFAULT_REGION")

            extra_vars += " ".join(map(lambda x: f"--var {x}", [
                f"aws_access_key_id={KEY_ID}",
                f"aws_secret_access_key={SECRET_KEY}",
                f"region={REGION}"
            ]))

        if provider == GCP:
            GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            extra_vars += " ".join(map(lambda x: f"--var {x}", [
                f"credentials_path={GOOGLE_APPLICATION_CREDENTIALS}"
            ]))

        return extra_vars
