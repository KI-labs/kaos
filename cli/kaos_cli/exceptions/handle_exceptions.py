import sys
from functools import singledispatch

import click
from kaos_cli.exceptions.exceptions import CommandError, SimpleApplicationError, WorkspaceExistsError, \
    InvalidWorkspaceError, NoTrainingJobsError, NoNotebookError, NoServingJobsError
from kaos_cli.utils.environment import format_missing_command_error


@singledispatch
def handle_specific_exception(e):
    pass


@handle_specific_exception.register(CommandError)
def _(e):
    error_message = '\n'.join(map(format_missing_command_error, e.commands))
    click.echo(error_message, err=True)


@handle_specific_exception.register(NoTrainingJobsError)
def _(e):
    click.echo("{} - There are currently {} training jobs - first run {}".format(
        click.style("Warning", bold=True, fg='yellow'),
        click.style('no', bold=True, fg='red'),
        click.style("kaos train deploy", bold=True, fg='green')))


@handle_specific_exception.register(NoServingJobsError)
def _(e):
    click.echo("{} - There are currently {} running endpoints - first run {}".format(
        click.style("Warning", bold=True, fg='yellow'),
        click.style('no', bold=True, fg='red'),
        click.style("kaos serve deploy", bold=True, fg='green')))


@handle_specific_exception.register(NoNotebookError)
def _(e):
    click.echo("{} - There are currently {} active notebooks - first run {}".format(
        click.style("Warning", bold=True, fg='yellow'),
        click.style('no', bold=True, fg='red'),
        click.style("kaos notebook deploy", bold=True, fg='green')))


@handle_specific_exception.register(WorkspaceExistsError)
def _(e):
    name = e.name
    click.echo("{} - Workspace {} already exists. Please use `{}` to select a workspace".format(
        click.style("Warning", bold=True, fg='yellow'),
        click.style(name, bold=True, fg='green'),
        click.style("kaos workspace set", bold=True, fg='white')))


@handle_specific_exception.register(InvalidWorkspaceError)
def _(e):
    click.echo(click.style(e.message, fg="red"), err=True)


@handle_specific_exception.register(SimpleApplicationError)
def _(e):
    click.echo(e.message, err=True)


@handle_specific_exception.register(IndexError)
def _(e):
    click.echo(str(e), err=True)


@handle_specific_exception.register(Exception)
def _(e):
    click.echo("{} - Unknown error: {}".format(
        click.style("Warning", bold=True, fg='yellow'),
        click.style(repr(e))), err=True)


def handle_exception(e):
    sys.exit(1)
