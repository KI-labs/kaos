import json
import os
import sys
import socket
from json import JSONDecodeError

import click
import textdistance
from kaos_cli.exceptions.exceptions import MissingArgumentError

from ..constants import KAOS_STATE_DIR, DOCKER, MINIKUBE, KAOS_TF_PATH


def validate_index(n: int, ind: int, command: str):
    """
    Simple function to validate existence of index within  in the model repository.

    Args:
        n (int): length of indices
        ind (int): selected index
        command (str): name of command for "tailored" help message
    """

    # ensure index exists in indices
    if -n <= ind < n:
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


def validate_build_env(cloud, env):
    """
    Simple validation of kaos build ENV

    Args:
        cloud (str): selected cloud backend
        env (str): selected ENV

    """

    try:
        if env and cloud in [DOCKER, MINIKUBE]:
            click.echo("{} - {} (-e/--env) is not applicable for {} deployment".format(
                click.style("Warning", bold=True, fg='yellow'),
                click.style("ENV", bold=True),
                click.style(cloud, bold=True, fg='red')))
            return None
        elif cloud in [DOCKER, MINIKUBE]:
            return None
        else:
            return 'prod' if not env else env  # default = prod
    except KeyError:
        click.echo('{} - Key Error'.format(click.style("Aborting", bold=True, fg='red')))
        sys.exit(1)


def validate_build_dir(path):
    """
    Ensure existence of kaos backend dir

    Args:
        path (str): path containing kaos backend dir

    """
    if not os.path.exists(path):
        cloud, *env = os.path.relpath(path, KAOS_TF_PATH).split('/')
        if env:
            click.echo("{} - {} [{}] backend in {} has not been deployed!".format(
                click.style("Warning", bold=True, fg='yellow'),
                click.style('kaos', bold=True),
                click.style(env[0], bold=True, fg='blue'),
                click.style(cloud, bold=True, fg='red')
            ))
        else:
            click.echo("{} - {} backend in {} has not been deployed!".format(
                click.style("Warning", bold=True, fg='yellow'),
                click.style('kaos', bold=True),
                click.style(cloud, bold=True, fg='red')
            ))
        sys.exit(1)


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
            # CHANGE BELOW
            return True

