import os

import click
from graphviz import Source
from kaos_cli.constants import SYM_CHECK
from kaos_cli.exceptions.handle_exceptions import handle_specific_exception, handle_exception
from kaos_cli.facades.serve_facade import ServeFacade
from kaos_cli.utils.custom_classes import NotRequiredIf, CustomHelpOrder
from kaos_cli.utils.decorators import init_check, workspace_check, health_check, pass_obj
from kaos_cli.utils.helpers import Compressor, Extractor
from kaos_cli.utils.rendering import render_table, render_queued_table
from kaos_cli.utils.validators import validate_inputs


# SERVE group
# ===========
@click.group(name='serve', cls=CustomHelpOrder,
             short_help='Deploy an {} with a trained model'.format(
                 click.style('endpoint', bold=True)))
@init_check
def serve():
    """
    Deploy an endpoint for serving trained ML models.
    """
    pass


# SERVE list
# ==========
@serve.command(name='list',
               short_help='List all running endpoints')
@health_check
@workspace_check
@pass_obj(ServeFacade)
def list_endpoint(facade: ServeFacade):
    """
    List all running endpoints.
    """
    try:
        data = facade.list()

        building_table, n_building = render_queued_table(data['building'],
                                                         header='BUILDING',
                                                         include_ind=False,
                                                         drop_cols={'progress'})

        running_table = ""
        n_running = len(data['endpoints'])
        running_jobs = data['endpoints']
        if n_running > 0:
            running_table = \
                f"\n{render_table(running_jobs, 'RUNNING', drop_cols={'code', 'image', 'model', 'progress'})}\n"

            facade.cache(running_jobs)

        if n_running + n_building > 30:
            click.echo_via_pager(f'{building_table}{running_table}')
        elif n_running + n_building > 0:
            click.echo(f'{building_table}{running_table}')
        else:
            click.echo("{} - There are currently {} running endpoints - first run {}".format(
                click.style("Warning", bold=True, fg='yellow'),
                click.style('no', bold=True, fg='red'),
                click.style("kaos serve deploy", bold=True, fg='green')))

    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)


# SERVE deploy
# ============
@serve.command(name='deploy',
               short_help='Configure and serve an ML model')
@click.option('-s', '--source_bundle', type=click.Path(exists=True, file_okay=False, dir_okay=True), required=True)
@click.option('-m', '--model_id', type=str, default=None, help='trained model id', required=False)
@click.option('--cpu', type=float, default=None, help="requested cpu (in cores or time)")
@click.option('--memory', type=str, default=None, help="requested memory (with allowed SI suffixes)")
@click.option('--gpu', type=int, default=0, help='requested number of gpu')
@health_check
@workspace_check
@pass_obj(ServeFacade)
def deploy_serve(facade: ServeFacade, source_bundle, model_id, cpu, memory, gpu):
    """
    Deploy endpoint with source (code + environment) and trained model id.
    """

    try:
        # inform user regarding source bundle "upload"
        click.echo("{} - Submitting {} bundle: {}".format(
            click.style("Info", bold=True, fg='green'),
            click.style('source', bold=True, fg='blue'),
            click.style(source_bundle, bold=True, fg='green', dim=True)))

        # process SOURCE bundle /inference/<name>/<model_id>
        with Compressor(label="Compressing source bundle", filename="source.zip", source_path=source_bundle) as c:
            data = facade.upload_source_bundle(c, model_id, cpu=cpu, memory=memory, gpu=gpu)

        # inform user regarding model_id "naming"
        if model_id:
            click.echo(" {} Adding trained {}: {}".format(
                click.style(SYM_CHECK, fg='green', bold=True),
                click.style("model_id", fg='blue', bold=True),
                click.style(model_id, fg='green', bold=True)))

        # inform user regarding source bundle "naming"
        source_glob = data['glob_name']
        click.echo(" {} Setting {} bundle: {}".format(
            click.style(SYM_CHECK, fg='green', bold=True),
            click.style("source", fg='blue', bold=True),
            click.style(f"/{source_glob}", fg='green', bold=True)))
    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)


# SERVE provenance
# ================
@serve.command(name='provenance',
               short_help='Retrieve endpoint details')
@click.option('-e', '--endpoint', type=str, help='name of the endpoint', cls=NotRequiredIf,
              not_required_if='ind')
@click.option('-i', '--ind', type=int, help='endpoint index', cls=NotRequiredIf,
              not_required_if='endpoint')
@click.option('-o', '--out_dir', default=os.getcwd(),
              type=click.Path(exists=False, file_okay=False, dir_okay=True), required=False)
@health_check
@workspace_check
@pass_obj(ServeFacade)
def endpoint_provenance(facade: ServeFacade, endpoint, ind, out_dir):
    """
    Retrieve provenance from a trained model.
    """
    # extract provenance via DAG
    try:

        # ensure arguments are correctly defined
        validate_inputs([endpoint, ind], ['endpoint', 'ind'])

        # selection by index
        if ind is not None:
            endpoint = facade.get_endpoint_by_ind(ind)

        click.echo("{} - Retrieving {} from {}".format(
            click.style("Info", bold=True, fg='green'),
            click.style("provenance", bold=True),
            click.style(endpoint, bold=True, fg='green', dim=True)))

        out_fid, data = facade.provenance(out_dir, endpoint)

        # render DAG (via dot)
        Source(data).render(out_fid)
        # remove raw DOT file
        os.remove(out_fid)

    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)


# SERVE get
# =========
@serve.command(name='get',
               short_help='Download source serving bundle (code and environment)')
@click.option('-e', '--endpoint', type=str, help='name of the endpoint', cls=NotRequiredIf,
              not_required_if='ind')
@click.option('-i', '--ind', type=int, help='endpoint index', cls=NotRequiredIf,
              not_required_if='endpoint')
@click.option('-o', '--out_dir', help='output directory', default=os.getcwd(),
              type=click.Path(exists=True, file_okay=False, dir_okay=True), required=False)
@health_check
@workspace_check
@pass_obj(ServeFacade)
def get_bundle(facade: ServeFacade, endpoint, ind, out_dir):
    """
    Download previously committed serving bundle (code + environment).
    """
    try:

        # ensure arguments are correctly defined
        validate_inputs([endpoint, ind], ['endpoint', 'ind'])

        # selection by index
        if ind is not None:
            endpoint = facade.get_endpoint_by_ind(ind)

        name, content = facade.get_bundle(endpoint)

        extractor = Extractor(out_dir, name, endpoint, label="Extracting serve bundle")
        click.echo("{} - Extracting {} bundle: {}".format(
            click.style("Info", bold=True, fg='green'),
            click.style('serve', bold=True, fg='blue'),
            click.style(extractor.workspace_out_dir, bold=True, fg='green', dim=True)))

        # build output directory (default = workspace)
        extractor(content)

    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)


# SERVE logs
# ==========
@serve.command(name="logs", short_help="Fetch logs from endpoint")
@click.option('-e', '--endpoint', type=str, help='name of the endpoint', cls=NotRequiredIf,
              not_required_if='ind')
@click.option('-i', '--ind', type=int, help='endpoint index', cls=NotRequiredIf,
              not_required_if='endpoint')
@click.option('-o', '--out_dir', default=os.getcwd(),
              type=click.Path(exists=True, file_okay=False, dir_okay=True),
              required=False, help='output directory')
@health_check
@workspace_check
@pass_obj(ServeFacade)
def get_logs(facade: ServeFacade, endpoint, ind, out_dir):
    """
    Retrieve logs from a running endpoint.
    """
    try:

        # ensure arguments are correctly defined
        validate_inputs([endpoint, ind], ['endpoint', 'ind'])

        # selection by index
        if ind is not None:
            endpoint = facade.get_endpoint_by_ind(ind)

        click.echo("{} - Retrieving {} from {}".format(
            click.style("Info", bold=True, fg='green'),
            click.style("logs", bold=True),
            click.style(endpoint, bold=True, fg='green', dim=True)))

        logs = facade.get_serve_logs(endpoint)
        click.echo_via_pager(logs)
        facade.write_serve_logs(endpoint, logs, out_dir)

    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)


# BUILD SERVE logs
# ================
@serve.command(name="build-logs", short_help="Fetch logs from endpoint build job")
@click.option('-j', '--job_id', type=str, help='job id', required=True)
@click.option('-o', '--out_dir', default=os.getcwd(),
              type=click.Path(exists=True, file_okay=False, dir_okay=True),
              required=False, help='output directory')
@health_check
@workspace_check
@pass_obj(ServeFacade)
def get_build_logs(facade: ServeFacade, job_id, out_dir):
    """
    Retrieve logs from a running endpoint.
    """
    try:

        # ensure arguments are correctly defined
        validate_inputs([job_id], ['ind'])

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


# SERVE kill
# ===========
@serve.command(name='kill',
               short_help='{}'.format(
                   click.style('Remove running endpoint', bold=True, fg='red')))
@click.option('-e', '--endpoint', type=str, help='name of the endpoint', cls=NotRequiredIf,
              not_required_if='ind')
@click.option('-i', '--ind', type=int, help='endpoint index', cls=NotRequiredIf,
              not_required_if='endpoint')
@health_check
@workspace_check
@pass_obj(ServeFacade)
def kill_endpoint(facade: ServeFacade, endpoint, ind):
    """
    Kill a running endpoint.
    """
    try:

        # ensure arguments are correctly defined
        validate_inputs([endpoint, ind], ['endpoint', 'ind'])

        # selection by index
        if ind is not None:
            endpoint = facade.get_endpoint_by_ind(ind)
        # confirm "kill"
        click.confirm('{} - Are you sure about killing endpoint {}?'.format(
            click.style("Warning", bold=True, fg='yellow'),
            click.style(endpoint, bold=True, fg='red')),
            abort=True)

        facade.delete(endpoint)

        click.echo('{} - Successfully killed endpoint {}'.format(
            click.style("Info", bold=True, fg='green'),
            click.style(endpoint, bold=True, fg='green')))

    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)
