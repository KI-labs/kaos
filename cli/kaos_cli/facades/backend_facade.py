import json
import os
import shutil
import uuid

import requests
from kaos_cli.constants import DOCKER, MINIKUBE, PROVIDER_DICT, AWS, BACKEND, INFRASTRUCTURE, GCP, LOCAL_CONFIG_DICT
from kaos_cli.exceptions.exceptions import HostnameError
from kaos_cli.services.state_service import StateService
from kaos_cli.services.terraform_service import TerraformService
from kaos_cli.utils.environment import check_environment
from distutils.dir_util import copy_tree


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

    @property
    def deployed_backend_list(self):
        return self.state_service.get(INFRASTRUCTURE, 'deployed_backend_list')

    def init(self, url, token):
        if not self.state_service.is_created():
            self.state_service.create()

        self.state_service.set(BACKEND, url=url, token=token)
        self.state_service.write()

    def build(self, provider, env, dir_build, local_backend=False, verbose=False):
        extra_vars = self._get_vars(provider)

        self.tf_service.set_verbose(verbose)
        directory = self._tf_init(provider, env, local_backend, destroying=False)
        self.tf_service.plan(directory, extra_vars)
        self.tf_service.apply(directory, extra_vars)

        url, kubeconfig = self._parse_config(dir_build)

        deployed_backend = provider + '_' + env

        # self.state_service.create()
        self.state_service.set(BACKEND, url=url, token=uuid.uuid4())
        self.state_service.set(INFRASTRUCTURE, kubeconfig=kubeconfig)
        print("debug_1")
        all_builds = self.state_service.get(INFRASTRUCTURE, 'deployed_backend_list')
        print("all_builds", all_builds)
        all_builds.append(deployed_backend)
        print("all_builds_after_append", all_builds)
        self.state_service.set(INFRASTRUCTURE, deployed_backend_list=all_builds)
        self.state_service.write()

    def destroy(self, provider, env, dir_build, verbose=False):
        extra_vars = self._get_vars(provider)

        self.tf_service.set_verbose(verbose)
        directory = self._tf_init(provider, env, local_backend=False, destroying=True)
        self._delete_resources()
        self.tf_service.destroy(directory, extra_vars)
        self._remove_build_files(dir_build)

    def is_created(self, dir_build):
        return self.state_service.is_created(dir_build)

    def _remove_build_files(self, dir_build):
        """
        Function to remove all "build" images
        """
        self.state_service.delete(dir_build)
        if os.path.exists(dir_build):
            shutil.rmtree(dir_build, ignore_errors=True)

    def _delete_resources(self):
        if self.state_service.has_section(BACKEND + '_' + self.cloud_env):
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
            self.tf_service.init(directory)
            if not self.tf_service.exists_workspace(directory, env):
                self.tf_service.new_workspace(directory, env)
            self.tf_service.select_workspace(directory, env)
        else:
            self.tf_service.init(directory)
        return directory

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
    def _get_vars(provider):
        out_dir = os.path.abspath(".")
        extra_vars = f"--var config_dir={out_dir} "

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
