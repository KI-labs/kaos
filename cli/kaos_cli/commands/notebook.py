import os

import click
from kaos_cli.constants import SYM_CHECK
from kaos_cli.exceptions.handle_exceptions import handle_specific_exception, handle_exception
from kaos_cli.facades.notebook_facade import NotebookFacade
from kaos_cli.utils.custom_classes import CustomHelpOrder, NotRequiredIf
from kaos_cli.utils.decorators import init_check, workspace_check, health_check, pass_obj
from kaos_cli.utils.helpers import Compressor
from kaos_cli.utils.rendering import render_table, render_queued_table
from kaos_cli.utils.validators import validate_inputs


def print_status_check(user):
    # inform user regarding source bundle "naming"
    click.echo("\n {} Notebook deployed - check status with {}".format(
        click.style(SYM_CHECK, bold=True, fg='green'),
        click.style("kaos notebook list", bold=True, fg='blue')))
    token = user.replace('.', '')  # TODO -> this is not ideal (fix given the internal callbacks)
    click.echo("{} - Please use \"{}\" as the notebook token".format(
        click.style("Info", bold=True, fg='green'),
        click.style(token, bold=True, fg="green")))


# NOTEBOOK group
# ==============
@click.group(name='notebook', cls=CustomHelpOrder,
             short_help='Deploy {} for building ML models'.format(click.style('notebook', bold=True)))
@init_check
def notebook():
    """
    Deploy a hosted notebook for experimentation and model generation.
    """
    pass


# NOTEBOOK list
# =============
@notebook.command(name='list',
                  short_help='List all available notebooks')
@health_check
@workspace_check
@pass_obj(NotebookFacade)
def list_notebooks(facade: NotebookFacade):
    """
    List all available running notebooks.
    """

    try:

        data = facade.list()

        building_table, n_building = render_queued_table(data['building'],
                                                         header='BUILDING',
                                                         include_ind=False,
                                                         drop_cols={'progress'})

        running_table = ""
        running_jobs = data['notebooks']
        n_running = len(running_jobs)
        if n_running > 0:
            running_table = \
                f"\n{render_table(running_jobs, 'RUNNING', drop_cols={'code', 'image', 'model', 'progress'})}\n"
            facade.cache(running_jobs)

        if n_running + n_building > 30:
            click.echo_via_pager(f'{building_table}{running_table}')
        elif n_running + n_building > 0:
            click.echo(f'{building_table}{running_table}')
        else:
            click.echo("{} - There are currently {} active notebooks - first run {}".format(
                click.style("Warning", bold=True, fg='yellow'),
                click.style('no', bold=True, fg='red'),
                click.style("kaos notebook deploy", bold=True, fg='green')))

    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)


# NOTEBOOK deploy
# ===============
@notebook.command(name='deploy',
                  short_help='Configure, start and connect to a notebook')
@click.option('-s', '--source_bundle', type=click.Path(exists=True, file_okay=False, dir_okay=True), required=False,
              help='directory containing notebook source bundle (environment)')
@click.option('-d', '--data_bundle', type=click.Path(exists=True, file_okay=False, dir_okay=True), required=False,
              help='directory containing desired data for experimentation')
@click.option('--cpu', type=float, default=None, help="requested cpu (in cores or time)")
@click.option('--memory', type=str, default="512Mi", help="requested memory (with allowed SI suffixes)")
@click.option('--gpu', type=int, default=0, help='requested number of gpu')
@health_check
@workspace_check
@pass_obj(NotebookFacade)
def deploy_notebook(facade: NotebookFacade, source_bundle, data_bundle, cpu, memory, gpu):
    """
    Configures and connects to a remote hosted Jupyter Notebook environment.
    """
    user = facade.user

    # process DATA bundle (POST /data/<name>/notebook)
    if data_bundle:
        click.echo("{} - Attaching {} bundle: {}".format(
            click.style("Info", bold=True, fg='green'),
            click.style('data', bold=True, fg='blue'),
            click.style(data_bundle, bold=True, fg='green', dim=True)))

        with Compressor(label="Compressing data bundle", filename="data.zip", source_path=data_bundle) as c:
            _ = facade.upload_data_bundle(c, cpu=cpu, memory=memory, gpu=gpu)

    # process SOURCE bundle (POST /notebook/<name>)
    if source_bundle:
        # inform user regarding source bundle "upload"
        click.echo("{} - Submitting {} bundle: {}".format(
            click.style("Info", bold=True, fg='green'),
            click.style('source', bold=True, fg='blue'),
            click.style(source_bundle, bold=True, fg='green', dim=True)))

        with Compressor(label="Compressing source bundle", filename="model.zip", source_path=source_bundle) as c:
            _ = facade.upload_source_bundle(c, cpu=cpu, memory=memory, gpu=gpu)
        print_status_check(user)

    if not source_bundle and not data_bundle:
        _ = facade.deploy(cpu=cpu, memory=memory, gpu=gpu)
        print_status_check(user)


# BUILD NOTEBOOK logs
# ====================
@notebook.command(name="build-logs", short_help="Fetch logs from notebook build job")
@click.option('-j', '--job_id', type=str, help='job id', required=True)
@click.option('-o', '--out_dir', default=os.getcwd(),
              type=click.Path(exists=True, file_okay=False, dir_okay=True),
              required=False, help='output directory')
@health_check
@workspace_check
@pass_obj(NotebookFacade)
def get_build_logs(facade: NotebookFacade, job_id, out_dir):
    """
    Retrieve logs from building notebook source image.
    """
    # get logs for a specific job

    try:
        # ensure arguments are correctly defined
        validate_inputs([job_id], ['job_id'])

        click.echo("{} - Retrieving {} from {}".format(
            click.style("Info", bold=True, fg='green'),
            click.style("build-logs", bold=True),
            click.style(job_id, bold=True, fg='green', dim=True)))

        logs = facade.get_build_logs(job_id)
        click.echo_via_pager(logs)
        facade.write_build_logs(job_id, logs, out_dir)

    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)


# NOTEBOOK kill
# =============
@notebook.command(name='kill',
                  short_help='{}'.format(click.style('Remove a running notebook', bold=True, fg='red')))
@click.option('-n', '--name', type=str, help='name of running notebook', cls=NotRequiredIf,
              not_required_if='ind')
@click.option('-i', '--ind', type=int, help='running notebook index', cls=NotRequiredIf,
              not_required_if='name')
@health_check
@workspace_check
@pass_obj(NotebookFacade)
def kill_notebook(facade: NotebookFacade, name, ind):
    """
    Kill a running notebook.
    """
    try:
        # ensure arguments are correctly defined
        validate_inputs([name, ind], ['name', 'ind'])

        # selection by index
        if ind is not None:
            name = facade.get_notebook_by_ind(ind)

        # confirm "kill"
        click.confirm('{} - Are you sure about killing notebook {}?'.format(
            click.style("Warning", bold=True, fg='yellow'),
            click.style(name, bold=True, fg='red')),
            abort=True)

        facade.delete(name)

        click.echo('{} - Successfully killed notebook {}'.format(
            click.style("Info", bold=True, fg='green'),
            click.style(name, bold=True, fg='green')))

    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)
