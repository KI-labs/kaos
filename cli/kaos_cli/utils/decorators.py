import os
import sys
from configparser import ConfigParser, ExtendedInterpolation

import click
import requests
from kaos_cli.utils.helpers import run_cmd

from ..constants import KAOS_STATE_DIR, CONFIG_PATH, ENV_DICT


def pass_obj(obj_id):
    def decorator(f):
        def new_func(*args, **kwargs):
            ctx = click.get_current_context()
            obj = ctx.obj[obj_id]

            if obj_id is None:
                raise RuntimeError('Managed to invoke callback without a '
                                   'context object of type %r existing'
                                   % obj_id)
            return ctx.invoke(f, obj, *args, **kwargs)

        return new_func

    return decorator


def pass_config(fun):
    def decorator(*args, **kwargs):
        ctx = click.get_current_context()
        state = ctx.obj['state']
        config = state.config

        return fun(config, *args, **kwargs)

    return decorator


def build_env_check(func):
    """
    Decorator for confirming the env vars are set.
    - Checks if the KAOS_HOME is set and is valid.
    - Checks if k8s cluster is setup and running for a local build.
    """

    def wrapper(*args, **kwargs):
        kaos_home_path = os.getenv("KAOS_HOME")
        if not kaos_home_path:
            click.echo("{} - Please set the KAOS_HOME environment variable to the source project directory".format(
                click.style("Warning", bold=True, fg='yellow')))
            sys.exit(1)

        kaos_config_path = kaos_home_path + "/.git/config"

        if not os.path.exists(kaos_config_path):
            click.echo("{} - Please ensure that KAOS_HOME points to a valid directory containing kaos".format(
                click.style("Warning", bold=True, fg='yellow')))
            sys.exit(1)

        line_list = [line.rstrip('\n') for line in open(kaos_config_path) if "KI-labs/kaos.git" in line]
        if not line_list:
            click.echo("{} - Please ensure that KAOS_HOME points to a valid directory containing kaos".format(
                click.style("Warning", bold=True, fg='yellow')))
            sys.exit(1)

        provider = kwargs["cloud"]

        if provider == "DOCKER":
            cmd = "kubectl get services --context docker-for-desktop"
            exitcode, out, err = run_cmd(cmd)
            if "command not found" in str(err):
                click.echo("{} - Docker Desktop not found. Please install any one of them and then retry build".format(
                    click.style("Warning", bold=True, fg='yellow')))
                sys.exit(1)
            if "Unable to connect to the server" in str(err):
                click.echo(
                    "{} - Kubernetes cluster is not enabled in the Docker Desktop or is not running. "
                    "Please ensure that a local k8 is running and then retry build".format(
                        click.style("Warning", bold=True, fg='yellow')))
                sys.exit(1)

        required_envs = list(filter(lambda e: not os.environ.get(e, None), ENV_DICT[provider]))
        if required_envs:
            click.echo("{} - Please set the following environment variables:".format(
                click.style("Warning", bold=True, fg='yellow')))
            for env in required_envs:
                click.echo("- {}".format((click.style(env, bold=True, fg='red'))))
            sys.exit(1)

        func(*args, **kwargs)

    return wrapper


def init_check(func):
    """
    Decorator for confirming the KAOS_STATE_DIR is present (i.e. initialized correctly).
    """

    def wrapper(*args, **kwargs):
        if not os.path.exists(KAOS_STATE_DIR):
            click.echo("{} - {} directory does not exist - first run {}".format(
                click.style("Warning", bold=True, fg='yellow'),
                click.style(os.path.split(KAOS_STATE_DIR)[-1], bold=True, fg='red'),
                click.style("kaos init", bold=True, fg='green')))
            sys.exit(1)
        if not os.path.exists(CONFIG_PATH):
            click.echo("{} - {} does not exist - run {}".format(
                click.style("Warning", bold=True, fg='yellow'),
                click.style("./kaos/config", bold=True, fg='red'),
                click.style("kaos init", bold=True, fg='green')))
            sys.exit(1)
        func(*args, **kwargs)

    return wrapper


def workspace_check(func):
    """
    Decorator for confirming <workspace> is defined in the CONFIG_PATH (i.e. kaos workspace set has been run).
    """

    def wrapper(*args, **kwargs):
        config = ConfigParser(interpolation=ExtendedInterpolation())
        config.read(CONFIG_PATH)

        if 'pachyderm' not in config:
            click.echo("{} - {} not defined - first run {}".format(
                click.style("Warning", bold=True, fg='yellow'),
                click.style("workspace", bold=True, fg='red'),
                click.style("kaos workspace set", bold=True, fg='green')))
            sys.exit(1)

        # get base_url
        base_url = config.get('backend', 'url')
        current_workspace = config.get('pachyderm', 'workspace')

        # GET all workspaces: /workspace
        r = requests.get(f"{base_url}/workspace")
        data = r.json()
        workspaces_list = [v for v in data['names']]

        if current_workspace not in workspaces_list:
            click.echo("{} - Workspace {} has been {}. \n\n"
                       "Please ensure the kaos train/serve commands are run on an active workspace. \n\n"
                       "Check available workspaces with - {}".format(
                click.style("Warning", bold=True, fg='yellow'),
                click.style(current_workspace, bold=True, fg='green'),
                click.style("deleted/killed", bold=True, fg='red'),
                click.style("kaos workspace list", bold=True, fg='green')))
            sys.exit(1)

        func(*args, **kwargs)

    return wrapper


def health_check(func):
    """
    Decorator for confirming endpoint is running.
    """

    def wrapper(*args, **kwargs):
        config = ConfigParser(interpolation=ExtendedInterpolation())
        config.read(CONFIG_PATH)

        # get base_url
        base_url = config.get('backend', 'url')

        try:
            func(*args, **kwargs)

        except (requests.exceptions.InvalidURL, requests.exceptions.InvalidSchema):
            click.echo("{} - Please run {} with a valid URL - {} is invalid!".format(
                click.style("Warning", bold=True, fg='yellow'),
                click.style("kaos init", bold=True, fg='green'),
                click.style(base_url, bold=True, fg='red')), err=True)
            sys.exit(1)

        except requests.exceptions.ConnectionError:
            click.echo("{} - Please ensure the endpoint is available - {} is unreachable!".format(
                click.style("Warning", bold=True, fg='yellow'),
                click.style(base_url, bold=True, fg='red')), err=True)
            sys.exit(1)

        except requests.exceptions.MissingSchema:
            click.echo("{} - Missing endpoint! Please set with - {}".format(
                click.style("Warning", bold=True, fg='yellow'),
                click.style("kaos init", bold=True, fg='green')), err=True)
            sys.exit(1)

    return wrapper
