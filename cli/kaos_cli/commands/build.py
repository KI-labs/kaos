import os
import sys

import click
from kaos_cli.constants import AWS, GCP, DOCKER, MINIKUBE
from kaos_cli.utils.validators import validate_build_env
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
def build(cloud, env, force, verbose, yes, local_backend):
    """
    Deploy kaos backend infrastructure based on the selected provider.
    """

    # Computing kaos state directory based on cloud and env before destroy
    build_path = f"state/{cloud}/{env}/" if cloud not in [DOCKER, MINIKUBE] else f"state/{cloud}/local/"

    dir_build = os.path.join(KAOS_STATE_DIR, build_path)

    # Creating build directory
    build_dir(dir_build)

    # validate ENV
    env = validate_build_env(cloud, env)

    @in_dir(dir_build)
    @pass_obj(BackendFacade)
    def __build_backend(backend: BackendFacade, cloud, env, force, verbose, yes, local_backend, dir_build):

        print("cloud", cloud)
        print("env", env)
        print("force", force)
        print("verbose", verbose)
        print("local_backend", local_backend)

        is_created = backend.is_created()

        if is_created and not force:
            click.echo('Aborting! - {} backend is already built.'.format(click.style("kaos", bold=True, fg='red')))
            sys.exit(1)

        elif is_created and force:
            click.echo('{} - Performing {} build of the backend'.format(
                click.style("Warning", bold=True, fg='yellow'),
                click.style("force", bold=True)))

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
                print("debug******")
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

        try:

            backend.build(cloud, env, dir_build, local_backend=local_backend, verbose=verbose)

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

            click.echo("Successfully built {} [{}] environment".format(click.style('kaos', bold=True, fg='green'),
                                                                       click.style(env, bold=True, fg='blue')))

            print("Azhor")

            if env:
                print("Prince")
                click.echo("{} - Successfully built {} [{}] environment".format(
                    click.style("Info", bold=True, fg='green'),
                    click.style('kaos', bold=True),
                    click.style(env, bold=True, fg='blue')))
            else:
                print("Ahai")
                click.echo("{} - Successfully built {} environment".format(
                    click.style("Info", bold=True, fg='green'),
                    click.style('kaos', bold=True)))

        except Exception as e:
            handle_specific_exception(e)
            handle_exception(e)

    __build_backend(cloud, env, force, verbose, yes, local_backend, dir_build)


@click.command(name='destroy',
               short_help='{}'.format(
                   click.style('Destroy the kaos backend', bold=True, fg='black')))
@click.option('-c', '--cloud', type=click.Choice([DOCKER, MINIKUBE, AWS, GCP]),
              help='selected provider', required=True)
@click.option('-e', '--env', type=click.Choice(['prod', 'stage', 'dev']),
              help='selected infrastructure environment', required=False)
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

    # validate ENV
    env = validate_build_env(cloud, env)

    @in_dir(dir_build)
    @pass_obj(BackendFacade)
    def __destroy_backend(backend: BackendFacade, cloud, env, dir_build, verbose, yes):
        if not yes:
            # confirm creation of backend
            if env:
                click.confirm('{} - Are you sure about destroying {} [{}] backend in {}?'.format(
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

            backend.destroy(cloud, env, dir_build, verbose=verbose)

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

    __destroy_backend(cloud, env, dir_build, verbose, yes)

