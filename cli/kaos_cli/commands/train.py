import os
import sys

import click
import prettytable
from graphviz import Source
from kaos_cli.constants import SYM_CHECK, SYM_CROSS, SYM_PROGRESS
from kaos_cli.exceptions.handle_exceptions import handle_specific_exception, handle_exception
from kaos_cli.facades.train_facade import TrainFacade
from kaos_cli.utils.custom_classes import NotRequiredIf, CustomHelpOrder, MutuallyExclusiveWith
from kaos_cli.utils.decorators import init_check, workspace_check, health_check, pass_obj
from kaos_cli.utils.helpers import Compressor, Extractor
from kaos_cli.utils.rendering import render_table, render_queued_table, render_job_info
from kaos_cli.utils.validators import validate_inputs, validate_manifest_file
from prettytable import PrettyTable


# TRAIN group
# =========
@click.group(name='train', cls=CustomHelpOrder,
             short_help='Run {} jobs with {} features'.format(
                 click.style('training', bold=True), click.style('ready-made', bold=True)))
@init_check
def train():
    """
    Train ML models with ready-made and split features.
    """
    pass


# TRAIN list
# ==========
@train.command(name='list',
               short_help='List all training jobs')
@health_check
@workspace_check
@pass_obj(TrainFacade)
def list_jobs(facade: TrainFacade):
    """
    List all training jobs.
    """

    try:

        data = facade.list()['response']

        building_table, n_building = render_queued_table(data['building'], header='BUILDING', include_ind=False,
                                                         drop_cols={'hyperopt', 'progress'})
        ingesting_table, n_ingesting = render_queued_table(data['ingesting'], header='INGESTING', include_ind=False,
                                                           drop_cols={'hyperopt'})

        training_table = ""
        n_training = len(data['training'])
        training_jobs = data['training']
        if n_training > 0:
            training_table = f"\n{render_table(training_jobs, 'TRAINING', drop_cols={'progress'})}\n"

            facade.cache(training_jobs)

        n_jobs = n_training + n_building + n_ingesting

        if n_jobs > 30:
            click.echo_via_pager(f'{ingesting_table}{building_table}{training_table}')
        elif n_jobs > 0:
            click.echo(f'{ingesting_table}{building_table}{training_table}')
        else:
            click.echo("{} - There are currently {} training jobs - first run {}".format(
                click.style("Warning", bold=True, fg='yellow'),
                click.style('no', bold=True, fg='red'),
                click.style("kaos train deploy", bold=True, fg='green')))

    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)


# TRAIN info
# ==========
@train.command(name='info',
               short_help='Describe a particular training job')
@click.option('-j', '--job_id', type=str, help='reference for the training job', cls=NotRequiredIf,
              not_required_if='ind')
@click.option('-i', '--ind', type=int, help='training job index', cls=NotRequiredIf,
              not_required_if='job_id')
@click.option('-s', '--sort_by', type=str, help='sort by metric', required=False)
@click.option('-p', '--page_id', type=str, help='page of the job list', required=False)
@health_check
@workspace_check
@pass_obj(TrainFacade)
def job_info(facade: TrainFacade, job_id, ind, sort_by, page_id):
    """
    Describe a training job.
    """
    try:

        # ensure arguments are correctly defined
        validate_inputs([job_id, ind], ['job_id', 'ind'])

        # selection by index
        if ind is not None:
            job_id = facade.get_job_by_ind(ind)

        click.echo("{} - Retrieving {} from {}".format(
            click.style("Info", bold=True, fg='green'),
            click.style("info", bold=True),
            click.style(job_id, bold=True, fg='green', dim=True)))

        data = facade.info(job_id, sort_by, page_id)

        formatted_info = render_job_info(data, sort_by)
        click.echo(formatted_info)

    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)


# TRAIN deploy
# ===========
@train.command(name='deploy',
               short_help='Configure and start training an ML model')
@click.option('-s', '--source_bundle', type=click.Path(exists=True, file_okay=False, dir_okay=True), required=False,
              help='directory containing training source bundle (code and environment)')
@click.option('-d', '--data_bundle', type=click.Path(exists=True, file_okay=False, dir_okay=True), required=False,
              help='directory containing data bundle (split features)', cls=MutuallyExclusiveWith,
              mutually_exclusive=['data_manifest'])
@click.option('-m', '--data_manifest', type=click.Path(exists=True, file_okay=True, dir_okay=False), required=False,
              help='data manifest file', cls=MutuallyExclusiveWith,
              mutually_exclusive=['data_bundle'])
@click.option('-h', '--hyperparams', type=click.Path(exists=True, file_okay=True, dir_okay=False), required=False,
              help='file containing hyperparameters')
@click.option('-p', '--parallelism', type=int,
              help="number of concurrent hyperopt training jobs")
@click.option('--cpu', type=float, default=None, help="requested cpu (in cores or time)")
@click.option('--memory', type=str, default=None, help="requested memory (with allowed SI suffixes)")
@click.option('--gpu', type=int, default=0, help='requested number of gpu')
@health_check
@workspace_check
@pass_obj(TrainFacade)
def deploy_job(facade: TrainFacade,
               source_bundle,
               data_bundle,
               data_manifest,
               hyperparams,
               parallelism,
               cpu,
               memory,
               gpu):
    """
    Deploy training job with source (code + environment) and/or data bundle (and hyperparameters).
    """

    try:

        # ensure either bundle exists
        if not source_bundle and not data_bundle and not data_manifest and not hyperparams:
            click.echo("{} - {} and/or {} and/or {} need to be defined for training"
                       .format(click.style('Warning', bold=True, fg='yellow'),
                               click.style('--source_bundle', bold=True, fg='green'),
                               click.style('--data_bundle or --data_manifest', bold=True, fg='green'),
                               click.style('--hyperparams', bold=True, fg='green')), err=True)
            sys.exit(1)

        # process SOURCE bundle (POST /train/<name>)
        if source_bundle:
            click.echo("{} - Submitting {} bundle: {}".format(
                click.style("Info", bold=True, fg='green'),
                click.style('source', bold=True, fg='blue'),
                click.style(source_bundle, bold=True, fg='green', dim=True)))

            with Compressor(label="Compressing source bundle", filename="model.zip", source_path=source_bundle) as c:
                data = facade.upload_source_bundle(c, cpu=cpu, memory=memory, gpu=gpu)

            # inform user regarding source bundle "naming"
            source_glob = data['glob_name']
            click.echo(" {} Setting {} bundle: {}\n".format(
                click.style(SYM_CHECK, fg='green', bold=True),
                click.style("source", fg='blue', bold=True),
                click.style(f"/{source_glob}", fg='green', bold=True))
            )

        # process DATA bundle (POST /data/<name>/features)
        if data_bundle:
            click.echo("{} - Submitting {} bundle: {}".format(
                click.style("Info", bold=True, fg='green'),
                click.style('data', bold=True, fg='blue'),
                click.style(data_bundle, bold=True, fg='green', dim=True)))

            with Compressor(label="Compressing data bundle", filename="data.zip", source_path=data_bundle) as c:
                data = facade.upload_data_bundle(c, cpu=cpu, memory=memory, gpu=gpu)

            # inform user regarding data bundle "naming"
            data_glob = data['glob_name']
            click.echo(" {} Setting {} bundle: {}\n".format(
                click.style(SYM_CHECK, fg='green', bold=True),
                click.style("data", fg='blue', bold=True),
                click.style(f"/{data_glob}", fg='green', bold=True))
            )

        # process DATA manifest (POST /data/<name>/manifest)
        if data_manifest:

            click.echo("{} - Submitting {} bundle: {}".format(
                click.style("Info", bold=True, fg='green'),
                click.style('data manifest', bold=True, fg='blue'),
                click.style(data_manifest, bold=True, fg='green', dim=True)))

            if validate_manifest_file(data_manifest):
                data = facade.upload_manifest(data_manifest, cpu=cpu, memory=memory, gpu=gpu)
            else:
                click.echo("The manifest file is invalid")
                sys.exit(1)

            # inform user regarding data manifest "naming"
            data_glob = data['glob_name']
            click.echo(" {} Setting {} bundle: {}\n".format(
                click.style(SYM_CHECK, fg='green', bold=True),
                click.style("data manifest", fg='blue', bold=True),
                click.style(f"/{data_glob}", fg='green', bold=True))
            )

        # process HYPERPARAMS (POST /data/<name>/params)
        if hyperparams:
            click.echo("{} - Submitting {} bundle: {}".format(
                click.style("Info", bold=True, fg='green'),
                click.style('hyperparams', bold=True, fg='blue'),
                click.style(hyperparams, bold=True, fg='green', dim=True)))

            data = facade.upload_hyperparams(hyperparams, cpu=cpu, memory=memory, gpu=gpu, parallelism=parallelism)
            hyper_glob = data['glob_name']

            click.echo(" {} Setting {} bundle: {}\n".format(
                click.style(SYM_CHECK, fg='green', bold=True),
                click.style("hyperparameters", fg='blue', bold=True),
                click.style(f"/{hyper_glob}/*", fg='green', bold=True))
            )

            # inform user regarding actual hyperopt jobs
            param_combinations = data['params']
            click.echo("{} {}\n".format(
                click.style("CURRENT HYPERPARAMETERS", fg='white', bold=True, underline=True),
                click.style(f"({len(param_combinations)})", fg='green', bold=True)))

            # set up simple table to iterate through response
            table = PrettyTable(hrules=prettytable.ALL)
            table.field_names = ['ind'] + list(param_combinations[0].keys())
            for ind, d in enumerate(param_combinations):
                table.add_row([ind] + list(d.values()))
            click.echo(f"{table.get_string()}\n")

        else:
            facade.upload_hyperparams(cpu=cpu, memory=memory, gpu=gpu, parallelism=parallelism)

        data = facade.inspect()

        # update status of pipeline (i.e. its inputs)
        data = [{
            "Image": f"{SYM_CHECK}\n{data['image']}" if data['image'].find('null') < 0 else SYM_CROSS,
            "Data": f"{SYM_CHECK}\n{data['data_glob']}" if data['data_glob'].find('null') < 0 else SYM_CROSS,
            "Hyperparams": f"{SYM_CHECK}\n{data['hyper_glob']}" if data['hyper_glob'].find('null') < 0 else SYM_CROSS,
        }]

        # overwrite if code was "added"
        if source_bundle:
            data[0]["Image"] = f"{SYM_PROGRESS}\n<building>"

        click.echo("{}\n".format(click.style("CURRENT TRAINING INPUTS", fg='white', bold=True, underline=True)))
        click.echo(render_table(data, include_ind=False))

    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)


# TRAIN get
# =========
@train.command(name='get',
               short_help='Download source job bundle (code, data, models)')
@click.option('-j', '--job_id', type=str, help='reference for the training job', cls=NotRequiredIf,
              not_required_if='ind')
@click.option('-i', '--ind', type=int, help='training job index', cls=NotRequiredIf,
              not_required_if='job_id')
@click.option('-o', '--out_dir', default=os.getcwd(),
              type=click.Path(exists=True, file_okay=False, dir_okay=True),
              required=False, help='output directory')
@click.option('-c', '--include_code', is_flag=True, default=False,
              help='include {} used for the training job'.format(click.style('code', fg='blue')))
@click.option('-d', '--include_data', is_flag=True, default=False,
              help='include {} used for the training job'.format(click.style('data', fg='blue')))
@click.option('-m', '--include_model', is_flag=True, default=False,
              help='include {} used for the training job'.format(click.style('model', fg='blue')))
@click.option('--model_id', type=str, default=None,
              help='filter trained models based on {}'.format(click.style('model_id', fg='blue')))
@health_check
@workspace_check
@pass_obj(TrainFacade)
def get_bundle(facade: TrainFacade, job_id, ind, out_dir, include_code, include_data, include_model, model_id):
    """
    Download previously committed training bundle (code, data, models).
    """
    try:
        # if no inputs -> get model and code
        if not (any([include_code, include_data, include_model])):
            include_code = True
            include_data = False
            include_model = True

        # ensure arguments are correctly defined
        validate_inputs([job_id, ind], ['job_id', 'ind'])

        # selection by index
        if ind is not None:
            job_id = facade.get_job_by_ind(ind)

        name, content = facade.get_bundle(job_id, include_code, include_data, include_model, model_id)

        extractor = Extractor(out_dir, name, job_id, label="Extracting train bundle")
        click.echo("{} - Extracting {} bundle: {}".format(
            click.style("Info", bold=True, fg='green'),
            click.style('train', bold=True, fg='blue'),
            click.style(extractor.workspace_out_dir, bold=True, fg='green', dim=True)))

        # build output directory (default = workspace)
        extractor(content)

    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)


# TRAIN provenance
# ================
@train.command(name='provenance',
               short_help='Retrieve training job provenance')
@click.option('-m', '--model_id', type=str, help='trained model id', required=True)
@click.option('-o', '--out_dir', default=os.getcwd(),
              type=click.Path(exists=False, file_okay=False, dir_okay=True), required=False)
@health_check
@workspace_check
@pass_obj(TrainFacade)
def job_provenance(facade: TrainFacade, model_id, out_dir):
    """
    Retrieve provenance from a trained model.
    """

    # extract provenance via DAG
    try:

        click.echo("{} - Retrieving {} from {}".format(
            click.style("Info", bold=True, fg='green'),
            click.style("provenance", bold=True),
            click.style(model_id, bold=True, fg='green', dim=True)))

        out, data = facade.provenance(out_dir, model_id)
        # render DAG (via dot)
        Source(data).render(out)
        os.remove(out)

    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)


# TRAIN logs
# ==========
@train.command(name="logs", short_help="Fetch training job logs")
@click.option('-j', '--job_id', type=str, help='reference for the training job', cls=NotRequiredIf,
              not_required_if='ind')
@click.option('-i', '--ind', type=int, help='training job index', cls=NotRequiredIf,
              not_required_if='job_id')
@click.option('-o', '--out_dir', default=os.getcwd(),
              type=click.Path(exists=True, file_okay=False, dir_okay=True),
              required=False, help='output directory')
@health_check
@workspace_check
@pass_obj(TrainFacade)
def get_logs(facade: TrainFacade, job_id, ind, out_dir):
    """
    Retrieve logs from a training job.
    """

    # build output directory (default = workspace)
    # get logs for a specific job
    try:

        # ensure arguments are correctly defined
        validate_inputs([job_id, ind], ['job_id', 'ind'])

        # selection by index
        if ind is not None:
            job_id = facade.get_job_by_ind(ind)

        click.echo("{} - Retrieving {} from {}".format(
            click.style("Info", bold=True, fg='green'),
            click.style("logs", bold=True),
            click.style(job_id, bold=True, fg='green', dim=True)))

        logs = facade.get_train_logs(job_id)
        click.echo_via_pager(logs)
        facade.write_train_logs(job_id, logs, out_dir)

    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)


# Kill TRAIN job provenance
# ==============
@train.command(name='kill',
               short_help='Kill training / build train job')
@click.option('-j', '--job_id', type=str, help='reference to the building job', required=True)
@health_check
@workspace_check
@pass_obj(TrainFacade)
def job_provenance(facade: TrainFacade, job_id):
    """
    Kill a running training / building train job.
    """

    try:
        facade.kill_job(job_id)
        click.echo("{} - Job {} successfully killed".format(
            click.style("Info", bold=True, fg='green'),
            click.style(job_id, bold=True, fg='green', dim=True)))

    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)
