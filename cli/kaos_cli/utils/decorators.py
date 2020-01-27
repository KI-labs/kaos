import os
import sys
from configobj import ConfigObj

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

            # Docker Desktop is running WITH single-node kubernetes cluster
            cmd = "kubectl get services --context docker-for-desktop"
            exitcode, out, err = run_cmd(cmd)
            error_codes = ["Unable to connect to the server",
                           "did you specify the right host or port?"]
            if any([e in str(err) for e in error_codes]):
                click.echo(
                    "{} - Docker Desktop with Kubernetes is currently {}\n\n"
                    "Please {} Docker Desktop and {} Kubernetes".format(
                        click.style("Warning", bold=True, fg='yellow'),
                        click.style("disabled", bold=True, fg='red'),
                        click.style("start", bold=True, fg='green'),
                        click.style("enable", bold=True, fg='green')))
                sys.exit(1)

            # Docker Desktop context is set
            cmd = "kubectl config current-context"
            exitcode, out, err = run_cmd(cmd)
            docker_contexts = ["docker-desktop", "docker-for-desktop"]
            if out.decode("utf-8").rstrip() not in docker_contexts:
                click.echo(
                    "{} - Cluster context {} set to Docker Desktop\n\n"
                    "Please run {}".format(
                        click.style("Warning", bold=True, fg='yellow'),
                        click.style("not", bold=True, fg='red'),
                        click.style("kubectl config use-context docker-desktop", bold=True, fg='green')))
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
        config = ConfigObj(CONFIG_PATH)

        if 'pachyderm' not in config:
            click.echo("{} - {} not defined - first run {}".format(
                click.style("Warning", bold=True, fg='yellow'),
                click.style("workspace", bold=True, fg='red'),
                click.style("kaos workspace set", bold=True, fg='green')))
            sys.exit(1)

        # get active context
        active_context = config['active']['environment']

        # get base_url
        base_url = config[active_context]['backend']['url']
        token = config[active_context]['backend']['token']
        current_workspace = config['pachyderm']['workspace']

        # GET all workspaces: /workspace
        r = requests.get(f"{base_url}/workspace", headers={"X-Token": token})
        if r.status_code == 401:
            click.echo("Unauthorized token")
            sys.exit(1)
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


def context_check(func):
    """
    Decorator for confirming an active_context is defined in the CONFIG_PATH (i.e. kaos build set has been run).
    """

    def wrapper(*args, **kwargs):
        config = ConfigObj(CONFIG_PATH)

        if 'active' not in config:
            click.echo("{} - {} not defined - first run {}".format(
                click.style("Warning", bold=True, fg='yellow'),
                click.style("active context", bold=True, fg='red'),
                click.style("kaos build set", bold=True, fg='green')))
            sys.exit(1)

        # get active context
        active_context = config['active']['environment']

        # GET all contexts
        contexts = config['contexts']['environments']

        def __validate_context(context, active_context):
            return context == active_context

        if isinstance(contexts, list):
            for context in contexts:
                active_context_exists = __validate_context(context, active_context)
        elif isinstance(contexts, str):
            active_context_exists = __validate_context(contexts, active_context)

        if not active_context_exists:
            click.echo("{} - Active context/build {} has been {}. \n\n"
                       "Please ensure the kaos build set is done on an existing/available deployment. \n\n"
                       "Check available contexts with - {}".format(
                click.style("Warning", bold=True, fg='yellow'),
                click.style(active_context, bold=True, fg='green'),
                click.style("destroyed", bold=True, fg='red'),
                click.style("kaos build list", bold=True, fg='green')))
            sys.exit(1)

        func(*args, **kwargs)

    return wrapper


def health_check(func):
    """
    Decorator for confirming endpoint is running.
    """

    def wrapper(*args, **kwargs):
        config = ConfigObj(CONFIG_PATH)

        # get active context
        active_context = config['active']['environment']

        # get base_url
        base_url = config[active_context]['backend']['url']

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
