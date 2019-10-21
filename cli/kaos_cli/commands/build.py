import os
import sys
import time

import click
from kaos_cli.exceptions.handle_exceptions import handle_specific_exception, handle_exception
from kaos_cli.facades.backend_facade import BackendFacade, is_cloud_provider
from kaos_cli.utils.decorators import build_env_check, pass_obj
from kaos_cli.constants import AWS, GCP, DOCKER, MINIKUBE, KAOS_STATE_DIR
from kaos_cli.utils.helpers import build_dir
from kaos_cli.utils.decorators import in_dir


# BUILD command
# =============
@click.command(name='build',
               short_help='{}'.format(
                   click.style('Build the kaos backend', bold=True, fg='black')))
@click.option('-c', '--cloud', type=click.Choice([DOCKER, MINIKUBE, AWS, GCP]),
              help='selected provider provider', required=True)
@click.option('-e', '--env', type=click.Choice(['prod', 'stage', 'dev']), default='prod',
              help='selected infrastructure environment', required=False)
@click.option('-f', '--force', is_flag=True,
              help='force building infrastructure', required=False)
@click.option('-v', '--verbose', is_flag=True,
              help='verbose output', required=False)
@click.option('-y', '--yes', is_flag=True,
              help='answer yes to any prompt', required=False)
@click.option('-l', '--local_backend', is_flag=True,
              help='terraform will store backend locally, only relevant for AWS and GCP', required=False)
@build_env_check
def build(cloud, env, force, verbose, yes, local_backend):
    """
    Deploy kaos backend infrastructure based on selected provider.
    """

    # Computing kaos state directory based on cloud and env before destroy
    build_path = f"state/{cloud}/{env}/" if cloud not in [DOCKER, MINIKUBE] else f"state/{cloud}/local/"

    dir_build = os.path.join(KAOS_STATE_DIR, build_path)

    # Creating build directory
    build_dir(dir_build)

    @in_dir(dir_build)
    @pass_obj(BackendFacade)
    def __build_backend(backend: BackendFacade, cloud, env, force, verbose, yes, local_backend, dir_build):
        is_created = backend.is_created()

        if is_created and not force:
            click.echo('Aborting! - {} backend is already built.'.format(click.style("kaos", bold=True, fg='red')))
            sys.exit(1)

        elif is_created and force:
            click.echo('Performing force build of the backend')

        if not yes:
            # confirm creation of backend
            click.confirm(
                'Are you sure about building {} [{}] backend in {}?'.format(click.style('kaos', bold=True, fg='green'),
                                                                            click.style(env, bold=True, fg='blue'),
                                                                            click.style(cloud, bold=True, fg='red')),
                abort=True)

        if local_backend:
            click.echo('Building with local backend! The terraform state exists only on this local machine!')

        if local_backend and cloud in [DOCKER, MINIKUBE]:
            click.echo(f'-l/--local_backend flag has been specified but cloud type is {cloud}, '
                       f'the flag has no effect as the backend is always local in this case.')

        try:

            backend.build(cloud, env, dir_build, local_backend=local_backend, verbose=verbose)

            if verbose:
                click.echo("Endpoint successfully set to {}".format(click.style(backend.url, bold=True, fg='green')))

            if is_cloud_provider(cloud):
                kubeconfig = os.path.abspath(backend.kubeconfig)
                click.echo("To interact with the Kubernetes cluster:\n\n {}"
                           .format(click.style("export KUBECONFIG=" + kubeconfig,
                                               bold=True, fg='red')))

            click.echo("Successfully built {} [{}] environment".format(click.style('kaos', bold=True, fg='green'),
                                                                       click.style(env, bold=True, fg='blue')))

        except Exception as e:
            handle_specific_exception(e)
            handle_exception(e)

    __build_backend(cloud, env, force, verbose, yes, local_backend, dir_build)


@click.command(name='destroy',
               short_help='{}'.format(
                   click.style('Destroy the kaos backend', bold=True, fg='black')))
@click.option('-c', '--cloud', type=click.Choice([DOCKER, MINIKUBE, AWS, GCP]),
              help='selected provider provider', required=True)
@click.option('-e', '--env', type=click.Choice(['prod', 'stage', 'dev']), default='prod',
              help='selected infrastructure environment', required=True)
@click.option('-v', '--verbose', is_flag=True,
              help='verbose output', required=False)
@click.option('-y', '--yes', is_flag=True,
              help='answer yes to any prompt', required=False)
@build_env_check
def destroy(cloud, env, verbose, yes):
    """
    Destroy kaos backend infrastructure based on selected provider.
    """
    # Computing kaos state directory based on cloud and env before destroy
    build_path = f"state/{cloud}/{env}/" if cloud not in [DOCKER, MINIKUBE] else f"state/{cloud}/local/"

    dir_build = os.path.join(KAOS_STATE_DIR, build_path)

    @in_dir(dir_build)
    @pass_obj(BackendFacade)
    def __destroy_backend(backend: BackendFacade, cloud, env, dir_build, verbose, yes):
        if not yes:
            # confirm creation of backend
            click.confirm(
                'Are you sure about destroying {} [{}] backend in {}?'.format(
                    click.style('kaos', bold=True, fg='green'),
                    click.style(env, bold=True, fg='blue'),
                    click.style(cloud, bold=True, fg='red')),
                abort=True)

        try:

            backend.destroy(cloud, env, dir_build, verbose=verbose)

            click.echo("Successfully destroyed {} [{}] environment".format(click.style('kaos', bold=True, fg='green'),
                                                                           click.style(env, bold=True, fg='blue')))

        except Exception as e:
            handle_specific_exception(e)
            handle_exception(e)

    __destroy_backend(cloud, env, dir_build, verbose, yes)

