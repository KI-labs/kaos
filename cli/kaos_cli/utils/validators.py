import json
import os
import sys
import socket
from json import JSONDecodeError
import shutil

import click
import textdistance
from kaos_cli.exceptions.exceptions import MissingArgumentError

from ..constants import KAOS_STATE_DIR, DOCKER, MINIKUBE, PROVIDER_DICT


class EnvironmentState:
    """
    This class is used to validate existence of already built environmnets
    """
    def __init__(self):
        self.cloud = None
        self.env = None
        self.build_dir = None
        self.tf_state_path = None
        self.provider_directory = None
        self.if_build_dir_exists = None
        self.if_tfstate_exists = None

    @classmethod
    def initialize(cls, cloud, env) -> "EnvironmentState":
        env_state = cls()
        env_state.cloud = cloud
        env_state.env = env

        infra_root = f"{PROVIDER_DICT.get(cloud)}"

        if is_cloud_provider(cloud):
            provider_directory = f"{infra_root}/{env}"
            build_dir = f"{infra_root}/__working_{env}"
            tf_state_path = f"{build_dir}/.terraform/terraform.tfstate"
            env_state.provider_directory = provider_directory

        else:
            build_dir = f"{infra_root}"
            tf_state_path = f"{build_dir}/terraform.tfstate"
            env_state.provider_directory = infra_root

        env_state.if_build_dir_exists = os.path.exists(build_dir)
        env_state.if_tfstate_exists = os.path.exists(tf_state_path)
        env_state.build_dir = build_dir
        env_state.tf_state_path = tf_state_path

        return env_state

    def validate_if_tf_state_exits(self) -> "EnvironmentState":
        """
        Ensure existence of kaos backend dir (tf_path) and throw appropriate warnings if it does not exist
        """
        if not self.if_tfstate_exists:
            if self.env:
                    click.echo("{} - {} [{}] backend in {} has not been deployed!".format(
                        click.style("Warning", bold=True, fg='yellow'),
                        click.style('kaos', bold=True),
                        click.style(self.env, bold=True, fg='blue'),
                        click.style(self.cloud, bold=True, fg='red')
                    ))
            elif not self.env:
                click.echo("{} - {} backend in {} has not been deployed!".format(
                    click.style("Warning", bold=True, fg='yellow'),
                    click.style('kaos', bold=True),
                    click.style(self.cloud, bold=True, fg='red')
                ))
            sys.exit(1)
        else:
            pass

    def set_build_env(self) -> "EnvironmentState":
        """
        Simple method to ensure the right env is set for local v cloud kaos build
        """

        if self.env and self.cloud in [DOCKER, MINIKUBE]:
            click.echo("{} - {} (-e/--env) is not applicable for {} deployment".format(
                click.style("Warning", bold=True, fg='yellow'),
                click.style("ENV", bold=True),
                click.style(self.cloud, bold=True, fg='red')))
            self.env = None
        elif self.cloud in [DOCKER, MINIKUBE]:
            self.env = None
        else:
            self.env = 'prod' if not self.env else self.env  # default = prod

    def remove_terraform_files(self) -> "EnvironmentState":
        """
        Simple method to remove existing terraform state for existing deployments
        """
        tf_dir_path = f"{self.build_dir}/.terraform"
        shutil.rmtree(tf_dir_path, ignore_errors=True)


def validate_index(n: int, ind: int, command: str):
    """
    Simple function to validate existence of index within  in the model repository.

    Args:
        n (int): length of indices
        ind (int): selected index
        command (str): name of command for "tailored" help message
    """

    # ensure index exists in indices
    if 0 <= ind < n:
        return ind
    else:
        raise IndexError(f"Index {ind} does not exist... Run `kaos {command} list` again")


def validate_cache(cache, command):
    """
    Simple function to validate cache is created (i.e. `kaos XXX list` was successfully run)

    Args:
        cache (str): path to local cache
        command (str): name of command for "tailored" help message
    """

    # ensure index exists in indices
    if not os.path.exists(cache):
        raise IndexError(f"Index not available until running `kaos {command} list`")
    else:
        with open(cache, 'r') as fp:
            return json.load(fp)


def validate_inputs(args, names):
    """
    Ensure all inputs are not None

    Args:
        args (list): input arguments
        names (list): input argument NAMES

    """
    if all([x is None for x in args]):
        raise MissingArgumentError(
            "Missing either {} as arguments...".format(click.style(' or '.join(names), bold=True)))


def validate_names(names: list, name: str, command: str):
    """
    Simple function to validate existence of name within names list.

    Args:
        names (list): selected index
        name (str): name
        command (str): name of command for "tailored" help message
    """

    if name not in names:
        raise IndexError(f"{command} {name} does not exist... Run `kaos {command} list` again")
    return name


def invalidate_cache(cache, workspace=False):
    """
    Invalidates cache by deleting current cache

    Args:
        cache (str): path to local cache
        workspace (bool): flag for removing all cache
    """

    # remove all cache when killing workspace
    if workspace:
        [os.remove(os.path.join(KAOS_STATE_DIR, f)) for f in os.listdir(KAOS_STATE_DIR) if f.endswith('.cache')]
    elif os.path.exists(cache):
        os.remove(cache)


def find_similar_term(term, dictionary):
    """
    Returns a list of terms similar to the given one according to the Damerau-Levenshtein distance

    https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance
    """
    return list(filter(lambda t: textdistance.damerau_levenshtein.distance(t, term) <= 2, dictionary))


def validate_manifest_file(file_name) -> bool:
    with open(file_name) as f:
        for l in f.readlines():
            try:
                d = json.loads(l)
                if not ('url' in d and 'path' in d):
                    return False
            except JSONDecodeError:
                return False
    return True


def validate_unused_port(port: int, host: str = '0.0.0.0') -> bool:
    """
    Validate that a specific network port is unused.

    Args:
        port (int): the integer port number to check
        host (str): hostip
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Try to bind to a port, if it raises a socket error, 
        # then return False; otherwise, return True
        try:
            s.bind((host, port))
            return True
        except socket.error:
            return False


def is_cloud_provider(cloud):
    return cloud not in (DOCKER, MINIKUBE)

