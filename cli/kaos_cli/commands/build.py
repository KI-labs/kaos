import os
import sys

import click
from kaos_cli.constants import AWS, GCP, DOCKER, MINIKUBE
from kaos_cli.exceptions.handle_exceptions import handle_specific_exception, handle_exception
from kaos_cli.facades.backend_facade import BackendFacade, is_cloud_provider
from typing import Optional

from kaos_cli.utils.helpers import build_dir
from kaos_cli.utils.custom_classes import CustomHelpOrder, NotRequiredIf
from kaos_cli.utils.decorators import build_env_check, pass_obj
from kaos_cli.utils.validators import validate_unused_port, validate_inputs, EnvironmentState
from kaos_cli.utils.rendering import render_table


# BUILD group
# =============
@click.group(name='build', cls=CustomHelpOrder,
             short_help='{} and its {}: {}, {}, {} and {}'.format(
                 click.style('Infrastructure deployments', bold=True),
                 click.style('sub-commands', bold=False),
                 click.style('deploy', bold=True),
                 click.style('list', bold=True),
                 click.style('set', bold=True),
                 click.style('active', bold=True)))
def build():
    """
    Build command allows you to deploy infrastructre and list the available deployments
    """
    pass


@build.command(name='deploy',
               short_help='{} the {} backend'.format(
                   click.style('Build', bold=True),
                   click.style('kaos', bold=True)))
@click.option('-c', '--cloud', type=click.Choice([DOCKER, MINIKUBE, AWS, GCP]),
              help='selected provider', required=True)
@click.option('-e', '--env', type=click.Choice(['prod', 'stage', 'dev']),
              help='selected environment [cloud only]', required=False)
@click.option('-f', '--force', is_flag=True,
              help='force build', required=False)
@click.option('-v', '--verbose', is_flag=True,
              help='verbose output', required=False)
@click.option('-y', '--yes', is_flag=True,
              help='answer yes to any prompt', required=False)
@click.option('-l', '--local_backend', is_flag=True,
              help='locally store terraform state [cloud only]', required=False)
@build_env_check
@pass_obj(BackendFacade)
def deploy(backend: BackendFacade, cloud: str, env: str, force: bool, verbose: bool, yes: bool, local_backend: bool):
    """
    Deploy kaos backend infrastructure based on selected provider.
    """

    env_state = EnvironmentState.initialize(cloud, env)

    if env_state.if_tfstate_exists and not force:
        click.echo('{} - {} backend is already built.'.format(click.style("Aborting", bold=True, fg='red'),
                                                              click.style("kaos", bold=True)))
        sys.exit(1)

    elif env_state.if_tfstate_exists and force:
        click.echo('{} - Performing {} build of the backend'.format(
            click.style("Warning", bold=True, fg='yellow'),
            click.style("force", bold=True)))
        env_state.remove_terraform_files()

    # set env variable appropriately
    env_state.set_build_env()
    cloud = env_state.cloud
    env = env_state.env

    if not yes:
        # confirm creation of backend
        if env_state.env:
            click.confirm(
                '{} - Are you sure about building {} [{}] backend in {}?'.format(
                    click.style("Warning", bold=True, fg='yellow'),
                    click.style('kaos', bold=True),
                    click.style(env_state.env, bold=True, fg='blue'),
                    click.style(env_state.cloud, bold=True, fg='red')),
                abort=True)
        else:
            click.confirm(
                '{} - Are you sure about building {} backend in {}?'.format(
                    click.style("Warning", bold=True, fg='yellow'),
                    click.style('kaos', bold=True),
                    click.style(env_state.cloud, bold=True, fg='red')),
                abort=True)

    if local_backend:
        click.echo('{} - Building with {} terraform backend state'.format(
            click.style("Info", bold=True, fg='green'),
            click.style("local", bold=True)))

    if local_backend and env_state.cloud in [DOCKER, MINIKUBE]:
        click.echo('{} - local backend (-l/--local_backend) has no effect for {}'.format(
            click.style("Info", bold=True, fg='green'),
            click.style(env_state.cloud, bold=True, fg='red')))

    # validate unused port for DOCKER
    if env_state.cloud == DOCKER and not validate_unused_port(80):
        # If the force build flag was set to True and the kaos backend 
        # was already built then skip the warning; otherwise, warn
        # the user that the port is already taken by another service
        # and issue a sys exit
        if not (force and env_state.if_tfstate_exists):
            click.echo(
                "{} - Network port {} is used but is needed for building {} backend in {}".format(
                    click.style("Warning", bold=True, fg='yellow'),
                    click.style("80", bold=True),
                    click.style("kaos", bold=True),
                    click.style(env_state.cloud, bold=True, fg='red')))
            sys.exit(1)
    
    try:
        is_built_successfully, env_state = backend.build(env_state.cloud,
                                                         env_state.env,
                                                         local_backend=local_backend,
                                                         verbose=verbose)

        if is_built_successfully:
            if verbose:
                click.echo("\n{} - Endpoint successfully set to {}".format(
                    click.style("Info", bold=True, fg='green'),
                    click.style(backend.url, bold=True, fg='green')))

            if is_cloud_provider(env_state.cloud):
                kubeconfig = os.path.abspath(backend.kubeconfig)
                click.echo("\n{} - To interact with the Kubernetes cluster:\n {}"
                           .format(click.style("Info", bold=True, fg='green'),
                                   click.style("export KUBECONFIG=" + kubeconfig,
                                               bold=True, fg='red')))

            if env:
                click.echo("{} - Successfully built {} [{}] environment".format(
                    click.style("Info", bold=True, fg='green'),
                    click.style('kaos', bold=True),
                    click.style(env, bold=True, fg='blue')))
            else:
                click.echo("{} - Successfully built {} environment".format(
                    click.style("Info", bold=True, fg='green'),
                    click.style('kaos', bold=True)))

        else:
            click.echo("{} - Deployment Unsuccessful while creating {} [{} {}] environment".format(
                click.style("Error", bold=True, fg='red'),
                click.style('kaos', bold=True),
                click.style(cloud, bold=True, fg='red'),
                click.style(env, bold=True, fg='red'))),
            sys.exit(1)

    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)


# build list
# =============
@build.command(name='list', short_help='List currently deployed backend builds')
@pass_obj(BackendFacade)
def list_all(backend: BackendFacade):
    """
    List all deployed kaos backend infrastructures.
    """
    try:
        available_contexts = backend.list()

        if available_contexts:
            backend.cache(available_contexts)
            table = render_table(available_contexts, include_ind=False)
            click.echo(table)
        else:
            click.echo("{} - No active builds found. Please run {} to deploy an environment".format(
                click.style("Warning", bold=True, fg='yellow'),
                click.style('kaos build deploy', bold=True, fg='green')))

    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)


# build set
# =============
@build.command(name='set', short_help='Set active build context')
@click.option('-c', '--context', type=str, help='set to a specific deployed context', cls=NotRequiredIf,
              not_required_if='ind')
@click.option('-i', '--ind', type=int, help='set to a specific deployed index', cls=NotRequiredIf,
              not_required_if='context')
@pass_obj(BackendFacade)
def set_active_context(backend: BackendFacade, context: Optional[str] = None, ind: Optional[int] = None):
    """
    Set current model environment workspace.
    """
    try:
        # ensure arguments are correctly defined
        validate_inputs([context, ind], ['context', 'ind'])
        # selection by index
        available_contexts = backend.list()
        if available_contexts:
            if context:
                is_context_set = backend.set_context_by_context(context)
                if not is_context_set:
                    click.echo('Context {} invalid. It is not one of the existing deployments in {} '
                               .format(click.style(context, bold=True, fg='red'), click.style("kaos", bold=True)))
                    sys.exit(1)
                click.echo("{} - Successfully set to context - {}".
                           format(click.style("Info", bold=True, fg='green'), click.style(context, bold=True, fg='green')))
            if ind or ind == 0:
                is_context_set, context = backend.set_context_by_index(ind)
                if not is_context_set:
                    click.echo('Index {} invalid. It is not one of the existing deployments in {} '
                               .format(click.style(str(ind), bold=True, fg='red'), click.style("kaos", bold=True)))
                    sys.exit(1)
                click.echo("{} - Successfully set to context - {}".
                           format(click.style("Info", bold=True, fg='green'), click.style(context, bold=True, fg='green')))
        else:
            click.echo("{} - No active builds found. Please run {} to deploy an environment".
                       format(click.style("Warning", bold=True, fg='yellow'),
                              click.style('kaos build deploy', bold=True, fg='green')))

    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)


# build active
# =============
@build.command(name='active', short_help='Display current/active context')
@pass_obj(BackendFacade)
def get_active_context(backend: BackendFacade):
    """
    Set current model environment workspace.
    """
    try:
        active_context = backend.get_active_context()

        if active_context:
            click.echo("{} - Active context is - {}".
                       format(click.style("Info", bold=True, fg='green'),
                              click.style(active_context, bold=True, fg='green')))
        else:
            available_contexts = backend.list()
            if available_contexts:
                click.echo("{} - No {} context set. Set an active context using `{}`".
                           format(click.style("Warning", bold=True, fg='yellow'),
                                  click.style("active", bold=True, fg='green'),
                                  click.style("kaos build set", bold=True, fg='white')))
            else:
                click.echo("{} - No active builds found. Please run {} to deploy an environment".format(
                    click.style("Warning", bold=True, fg='yellow'),
                    click.style('kaos build deploy', bold=True, fg='green')))

    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)


@click.command(name='destroy',
               short_help='{} the {} backend'.format(
                   click.style('Destroys', bold=True),
                   click.style('kaos', bold=True)))
@click.option('-c', '--cloud', type=click.Choice([DOCKER, MINIKUBE, AWS, GCP]),
              help='selected provider provider', required=True)
@click.option('-e', '--env', type=click.Choice(['prod', 'stage', 'dev']),
              help='selected infrastructure environment', required=False)
@click.option('-v', '--verbose', is_flag=True,
              help='verbose output', required=False)
@click.option('-y', '--yes', is_flag=True,
              help='answer yes to any prompt', required=False)
@build_env_check
@pass_obj(BackendFacade)
def destroy(backend: BackendFacade, cloud, env, verbose, yes):
    """
    Destroy kaos backend infrastructure based on selected provider.
    """
    env_state = EnvironmentState.initialize(cloud, env)

    # set env variable appropriately
    env_state.set_build_env()

    # Ensure that appropriate warnings are displayed
    env_state.validate_if_tf_state_exits()

    if not yes:
        # confirm creation of backend
        if env_state.env:
            click.confirm(
                '{} - Are you sure about destroying {} [{}] backend in {}?'.format(
                    click.style("Warning", bold=True, fg='yellow'),
                    click.style('kaos', bold=True),
                    click.style(env_state.env, bold=True, fg='blue'),
                    click.style(env_state.cloud, bold=True, fg='red')),
                abort=True)
        else:
            click.confirm(
                '{} - Are you sure about destroying {} backend in {}?'.format(
                    click.style("Warning", bold=True, fg='yellow'),
                    click.style('kaos', bold=True),
                    click.style(env_state.cloud, bold=True, fg='red')),
                abort=True)
    try:

        env_state = backend.destroy(env_state, verbose=verbose)

        if not env_state.if_tfstate_exists:
            if env_state.env:
                click.echo(
                    "{} - Successfully destroyed {} [{}] environment".format(click.style("Info", bold=True, fg='green'),
                                                                             click.style('kaos', bold=True),
                                                                             click.style(env_state.env, bold=True, fg='blue')))
            else:
                click.echo(
                    "{} - Successfully destroyed {} environment".format(click.style("Info", bold=True, fg='green'),
                                                                        click.style('kaos', bold=True)))
        else:
            if env_state.env:
                click.echo("{} - Destroy operation unsuccessful for {} [{} {}] environment".format(
                    click.style("Error", bold=True, fg='red'),
                    click.style('kaos', bold=True),
                    click.style(env_state.cloud, bold=True, fg='red'),
                    click.style(env_state.env, bold=True, fg='red'))),
                sys.exit(1)
            else:
                click.echo("{} - Destroy operation unsuccessful for {} [{}] environment".format(
                    click.style("Error", bold=True, fg='red'),
                    click.style('kaos', bold=True),
                    click.style(env_state.cloud, bold=True, fg='red'))),
                sys.exit(1)

    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)
