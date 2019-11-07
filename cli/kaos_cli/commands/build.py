import os
import sys

import click
from kaos_cli.constants import AWS, GCP, DOCKER, MINIKUBE
from kaos_cli.exceptions.handle_exceptions import handle_specific_exception, handle_exception
from kaos_cli.facades.backend_facade import BackendFacade, is_cloud_provider

from kaos_cli.utils.custom_classes import CustomHelpOrder, NotRequiredIf
from kaos_cli.utils.decorators import build_env_check, pass_obj
from kaos_cli.utils.validators import validate_build_env, validate_unused_port, validate_inputs
from kaos_cli.utils.rendering import render_table


# BUILD group
# =============

@click.group(name='build', cls=CustomHelpOrder,
             short_help=' {} and its {} '.format(
                 click.style('build', bold=True), click.style('sub-commands', bold=True)))
def build():
    """
    Build command allows you to deploy infrastructre and list the available deployments
    """
    pass


@build.command(name='deploy',
               short_help='{}'.format(
                   click.style('Build the kaos backend', bold=True, fg='black')))
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
def deploy(backend: BackendFacade, cloud, env, force, verbose, yes, local_backend):
    """
    Deploy kaos backend infrastructure based on selected provider.
    """

    is_created = backend.is_created()

    if is_created and not force:
        click.echo('{} - {} backend is already built.'.format(click.style("Aborting", bold=True, fg='red'),
                                                              click.style("kaos", bold=True)))
        sys.exit(1)

    elif is_created and force:
        click.echo('{} - Performing {} build of the backend'.format(
            click.style("Warning", bold=True, fg='yellow'),
            click.style("force", bold=True)))

    # validate ENV
    env = validate_build_env(cloud, env)

    if not yes:
        # confirm creation of backend
        if env:
            click.confirm(
                '{} - Are you sure about building {} [{}] backend in {}?'.format(
                    click.style("Warning", bold=True, fg='yellow'),
                    click.style('kaos', bold=True),
                    click.style(env, bold=True, fg='blue'),
                    click.style(cloud, bold=True, fg='red')),
                abort=True)
        else:
            click.confirm(
                '{} - Are you sure about building {} backend in {}?'.format(
                    click.style("Warning", bold=True, fg='yellow'),
                    click.style('kaos', bold=True),
                    click.style(cloud, bold=True, fg='red')),
                abort=True)

    if local_backend:
        click.echo('{} - Building with {} terraform backend state'.format(
            click.style("Info", bold=True, fg='green'),
            click.style("local", bold=True)))

    if local_backend and cloud in [DOCKER, MINIKUBE]:
        click.echo('{} - local backend (-l/--local_backend) has no effect for {}'.format(
            click.style("Info", bold=True, fg='green'),
            click.style(cloud, bold=True, fg='red')))

    # validate unused port for DOCKER
    if cloud == DOCKER and not validate_unused_port(80):
        # If the force build flag was set to True and the kaos backend 
        # was already built then skip the warning; otherwise, warn
        # the user that the port is already taken by another service
        # and issue a sys exit
        if not (force and backend.is_created()):
            click.echo(
                "{} - Network port {} is used but is needed for building {} backend in {}".format(
                    click.style("Warning", bold=True, fg='yellow'),
                    click.style("80", bold=True),
                    click.style("kaos", bold=True),
                    click.style(cloud, bold=True, fg='red')))
            sys.exit(1)
    
    try:

        backend.build(cloud, env, local_backend=local_backend, verbose=verbose)

        if verbose:
            click.echo("\n{} - Endpoint successfully set to {}".format(
                click.style("Info", bold=True, fg='green'),
                click.style(backend.url, bold=True, fg='green')))

        if is_cloud_provider(cloud):
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
        if len(available_contexts) > 0:
            backend.cache(available_contexts)
            table = render_table(available_contexts, include_ind=False)
            click.echo(table)

    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)


# build set
# =============
@build.command(name='set', short_help='Set active build context')
@click.option('-c', '--context', type=str, help='set to a specific deployed context', cls=NotRequiredIf,
              not_required_if='ind')
@click.option('-i', '--ind', type=str, help='set to a specific deployed index', cls=NotRequiredIf,
              not_required_if='context')
@pass_obj(BackendFacade)
def set_active_context(backend: BackendFacade, context, ind):
    """
    Set current model environment workspace.
    """
    try:
        # ensure arguments are correctly defined
        validate_inputs([context, ind], ['context', 'ind'])
        # selection by index
        if context:
            set = backend.set_context_by_context(context)
            if not set:
                click.echo('Context {} invalid. It is not one of the existing deployments in {} '
                           .format(click.style(context, bold=True, fg='red'), click.style("kaos", bold=True)))
                sys.exit(1)
        if ind:
            set = backend.set_context_by_index(ind)
            if not set:
                click.echo('Index {} invalid. It is not one of the existing deployments in {} '
                           .format(click.style(context, bold=True, fg='red'), click.style("kaos", bold=True)))
                sys.exit(1)

    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)


@click.command(name='destroy',
               short_help='{}'.format(
                   click.style('Destroy the kaos backend', bold=True, fg='black')))
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

    # validate ENV
    env = validate_build_env(cloud, env)

    if not yes:
        # confirm creation of backend
        if env:
            click.confirm(
                '{} - Are you sure about destroying {} [{}] backend in {}?'.format(
                    click.style("Warning", bold=True, fg='yellow'),
                    click.style('kaos', bold=True),
                    click.style(env, bold=True, fg='blue'),
                    click.style(cloud, bold=True, fg='red')),
                abort=True)
        else:
            click.confirm(
                '{} - Are you sure about destroying {} backend in {}?'.format(
                    click.style("Warning", bold=True, fg='yellow'),
                    click.style('kaos', bold=True),
                    click.style(cloud, bold=True, fg='red')),
                abort=True)
    try:

        backend.destroy(cloud, env, verbose=verbose)

        if env:
            click.echo(
                "{} - Successfully destroyed {} [{}] environment".format(click.style("Info", bold=True, fg='green'),
                                                                         click.style('kaos', bold=True),
                                                                         click.style(env, bold=True, fg='blue')))
        else:
            click.echo(
                "{} - Successfully destroyed {} environment".format(click.style("Info", bold=True, fg='green'),
                                                                    click.style('kaos', bold=True)))

    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)
