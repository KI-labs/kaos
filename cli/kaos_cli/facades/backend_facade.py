import json
import os
import shutil
import uuid
from distutils.dir_util import copy_tree

import requests
from kaos_cli.constants import DOCKER, MINIKUBE, AWS, BACKEND, INFRASTRUCTURE, GCP, LOCAL_CONFIG_DICT, \
    CONTEXTS, ACTIVE, BACKEND_CACHE, DEFAULT, USER, REMOTE, KAOS_STATE_DIR
from kaos_cli.exceptions.exceptions import HostnameError
from kaos_cli.services.state_service import StateService
from kaos_cli.services.terraform_service import TerraformService
from kaos_cli.utils.environment import check_environment
from kaos_cli.utils.helpers import build_dir
from kaos_cli.utils.validators import EnvironmentState, is_cloud_provider


class BackendFacade:
    """
    This class should handle all backend related configuration and settings.
    """

    def __init__(self, state_service: StateService, terraform_service: TerraformService):
        self.state_service = state_service
        self.tf_service = terraform_service

    @property
    def active_context(self):
        return self.state_service.get(ACTIVE, 'environment')

    @property
    def url(self):
        return self.state_service.get_section(self.active_context, BACKEND, 'url')

    @property
    def user(self):
        return self.state_service.get(DEFAULT, 'user')

    @property
    def token(self):
        return self.state_service.get_section(self.active_context, BACKEND, 'token')

    @property
    def kubeconfig(self):
        return self.state_service.get_section(self.active_context, INFRASTRUCTURE, 'kubeconfig')

    def init(self, url, auth_token):
        if not self.state_service.is_created(KAOS_STATE_DIR):
            self.state_service.create()

        self.state_service.set(DEFAULT, user=USER)
        self._set_context_list(REMOTE)
        self._set_active_context(REMOTE)
        self.state_service.set(REMOTE)
        self.state_service.set_section(REMOTE, BACKEND, url=url, token=auth_token)
        self.state_service.write()

    def is_created(self):
        return self.state_service.is_created(KAOS_STATE_DIR)

    def list(self):
        try:
            contexts = self.state_service.get(CONTEXTS, 'environments')
            contexts_info = self.jsonify_context_list(contexts)
            return contexts_info

        except KeyError:
            return []

    def get_active_context(self):
        try:
            active_context = self.state_service.get(ACTIVE, 'environment')
            return active_context

        except KeyError:
            return None

    @staticmethod
    def get_context_info(context, index):
        try:
            cloud, env = context.split('_')
        except ValueError:
            cloud = context
            env = None
        env = "local" if not env else env
        info = {
            "index": index,
            "context": context,
            "provider": cloud,
            "env": env
        }
        return info

    @staticmethod
    def get_context_by_index(context_info, index):
        for context in context_info:
            if context['index'] == index:
                return context['context']

    def jsonify_context_list(self, contexts):
        contexts_info = []
        index = 0
        if isinstance(contexts, list):
            for context in contexts:
                contexts_info.append(self.get_context_info(context, index))
                index = index + 1

        elif isinstance(contexts, str):
            contexts_info.append(self.get_context_info(contexts, index))
        return contexts_info

    def set_context_by_context(self, current_context):
        context_info = self.list()
        for context in context_info:
            if context['context'] == current_context:
                self._set_active_context(current_context)
                self.state_service.write()
                return True
        return False

    def set_context_by_index(self, index):
        context_info = self.list()
        current_context = self.get_context_by_index(context_info, index)
        if current_context:
            self._set_active_context(current_context)
            self.state_service.write()
            return True, current_context
        return False, current_context

    def build(self, provider, env, local_backend=False, verbose=False):
        env_state = EnvironmentState.initialize(provider, env)

        if not os.path.exists(env_state.build_dir):
            build_dir(env_state.build_dir)

        auth_token = uuid.uuid4()
        extra_vars = self._get_vars(provider, env_state.build_dir, auth_token)

        self.tf_service.cd_dir(env_state.build_dir)
        self.tf_service.set_verbose(verbose)
        self._tf_init(env_state, provider, env, local_backend, destroying=False)
        self.tf_service.plan(env_state.build_dir, extra_vars)
        self.tf_service.apply(env_state.build_dir, extra_vars)
        self.tf_service.execute()

        # check if the deployed successfully
        # Refresh environment states after terraform service operations
        env_state = EnvironmentState.initialize(provider, env)

        if env_state.if_tfstate_exists:
            url, kubeconfig = self._parse_config(env_state.build_dir)
            current_context = provider if provider in [DOCKER, MINIKUBE] else f"{provider}_{env}"
            self.state_service.set(DEFAULT, user=USER)
            self._set_context_list(current_context)
            self._set_active_context(current_context)
            self.state_service.set(current_context)
            self.state_service.set_section(current_context, BACKEND,
                                           url=url, token=auth_token)
            self.state_service.set_section(current_context, INFRASTRUCTURE,
                                           kubeconfig=kubeconfig)
            self.state_service.write()
            return True, env_state

        return False, env_state

    def destroy(self, env_state, verbose=False):
        extra_vars = self._get_vars(env_state.cloud, env_state.build_dir)
        self.tf_service.cd_dir(env_state.build_dir)

        self.tf_service.set_verbose(verbose)

        self._tf_init(env_state, env_state.cloud, env_state.env, local_backend=False, destroying=True)

        current_context = env_state.cloud if env_state.cloud in [DOCKER, MINIKUBE] \
            else env_state.cloud + '_' + env_state.env

        self._delete_resources(current_context)
        self._unset_context_list(current_context)
        self._remove_section(current_context)
        self._deactivate_context()
        self.tf_service.destroy(env_state.build_dir, extra_vars)
        self.tf_service.execute()
        self._remove_build_files(env_state.build_dir)
        self.state_service.write()
        # check if the infra is destroyed successfully
        # Refresh environment states after terraform service operations
        env_state = EnvironmentState.initialize(env_state.cloud, env_state.env)
        # set env variable appropriately
        env_state.set_build_env()
        return env_state

    def _remove_build_files(self, dir_build):
        """
        Function to remove backend directory
        """
        self.state_service.provider_delete(dir_build)
        if not self.state_service.list_providers():
            self.state_service.full_delete(dir_build)

    def _delete_resources(self, context):
        if self.state_service.has_section(context, BACKEND):
            requests.delete(f"{self.url}/internal/resources")

    def _tf_init(self, env_state, provider, env, local_backend, destroying=False):
        check_environment(provider)
        if is_cloud_provider(provider):
            if not destroying or not os.path.isdir(env_state.build_dir):
                copy_tree(env_state.provider_directory, env_state.build_dir)
            if local_backend:
                shutil.copy(LOCAL_CONFIG_DICT.get(provider), env_state.build_dir)

            # simply always create the workspace
            self.tf_service.init(env_state.build_dir)
            self.tf_service.new_workspace(env_state.build_dir, env)
            self.tf_service.select_workspace(env_state.build_dir, env)
        else:
            copy_tree(env_state.provider_directory, env_state.build_dir)
            self.tf_service.init(env_state.build_dir)

    def _set_context_list(self, current_context):
        try:
            contexts = self.state_service.get(CONTEXTS, 'environments')
        except KeyError:
            contexts = ''

        updated_contexts = []

        if isinstance(contexts, list):
            if current_context not in contexts:
                contexts.append(current_context)
            updated_contexts = contexts
        elif isinstance(contexts, str) or not contexts:
            # check if current context is the same as existing context
            if current_context != contexts:
                # There is only one context or no context in available contexts
                if contexts:
                    # exactly one available context
                    updated_contexts.append(contexts)
                    updated_contexts.append(current_context)
                else:
                    # no available context
                    updated_contexts.append(current_context)

        self.state_service.set(CONTEXTS, environments=updated_contexts)

    def _unset_context_list(self, current_context):
        try:
            contexts = self.state_service.get(CONTEXTS, 'environments')
        except KeyError:
            contexts = ''

        updated_contexts = []

        if isinstance(contexts, list):
            contexts.remove(current_context)
            updated_contexts = contexts

        # If the available contexts is exactly equal to one or none, then simply update empty list
        self.state_service.set(CONTEXTS, environments=updated_contexts)

    def _set_active_context(self, current_context):
        self.state_service.set(ACTIVE, environment=current_context)

    def _remove_section(self, current_context):
        config = self.state_service.config
        try:
            del config[current_context]
        except KeyError:
            pass
        self.state_service.config = config

    def _deactivate_context(self):
        self.state_service.set(ACTIVE, environment=None)
        self.state_service.write()

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
    def _get_vars(provider, dir_build, auth_token=None):
        extra_vars = f"--var config_dir={dir_build} --var token={auth_token} "

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
