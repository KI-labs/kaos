import click
import sys

from kaos_cli.exceptions.handle_exceptions import handle_specific_exception, handle_exception
from kaos_cli.facades.workspace_facade import WorkspaceFacade
from kaos_cli.utils.custom_classes import NotRequiredIf, CustomHelpOrder
from kaos_cli.utils.decorators import init_check, workspace_check, health_check, pass_obj, context_check
from kaos_cli.utils.rendering import render_table
from kaos_cli.utils.validators import validate_inputs


# WORKSPACE group
# ===============
@click.group(name='workspace', cls=CustomHelpOrder,
             short_help='Organize and {} ML environments'.format(
                 click.style('separate', bold=True)))
@init_check
def workspace():
    """
    Organize and separate model environment by workspace.
    """
    pass


# WORKSPACE list
# ==============
@workspace.command(name='list',
                   short_help='List all available workspaces')
@context_check
@health_check
@pass_obj(WorkspaceFacade)
def list_workspaces(facade: WorkspaceFacade):
    """
    List all available workspaces.
    """
    try:
        workspaces = facade.list()
        if len(workspaces) > 0:

            facade.cache(workspaces)
            table = render_table(workspaces)
            click.echo(table)

        else:
            click.echo("{} - There are currently {} active workspaces - first run {}".format(
                click.style("Warning", bold=True, fg='yellow'),
                click.style('no', bold=True, fg='red'),
                click.style("kaos workspace create", bold=True, fg='green')))

    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)


# WORKSPACE set
# =============
@workspace.command(name='set',
                   short_help='Set current workspace')
@click.option('-n', '--name', type=str, help='available workspace name', cls=NotRequiredIf,
              not_required_if='ind')
@click.option('-i', '--ind', type=int, help='workspace index', cls=NotRequiredIf,
              not_required_if='name')
@context_check
@health_check
@pass_obj(WorkspaceFacade)
def set_workspace(facade: WorkspaceFacade, name, ind):
    """
    Set current model environment workspace.
    """

    try:

        # ensure arguments are correctly defined
        validate_inputs([name, ind], ['name', 'ind'])

        # selection by index
        if ind is not None:
            name = facade.get_workspace_by_ind(ind)

        if facade.exists_by_name(name):
            facade.set_by_name(name)

            click.echo("{} - Successfully set {} workspace".format(
                click.style("Info", bold=True, fg='green'),
                click.style(name, bold=True, fg='green')))

        else:
            similar = facade.find_similar_workspaces(name)

            if similar:
                click.echo("{} - Workspace {} does not exist. Did you mean one of these?".format(
                    click.style("Warning", bold=True, fg='yellow'),
                    click.style(name, bold=True, fg='green')))
                click.echo('\n'.join(map(lambda t: click.style(t, bold=True, fg='red'), similar)))
            else:
                click.echo("{} - Workspace {} does not exist. Check the existing workspaces with `{}`".format(
                    click.style("Warning", bold=True, fg='yellow'),
                    click.style(name, bold=True, fg='green'),
                    click.style("kaos workspace list", bold=True, fg='white')))

    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)


# WORKSPACE create
# ================
@workspace.command(name='create',
                   short_help='Create a new workspace')
@click.option('-n', '--name', type=str,
              help='new workspace name')
@context_check
@health_check
@pass_obj(WorkspaceFacade)
def create_workspace(facade: WorkspaceFacade, name):
    """
    Creates a workspace.
    """

    try:
        facade.create(name)

        click.echo("{} - Successfully set {} workspace".format(
            click.style("Info", bold=True, fg='green'),
            click.style(name, bold=True, fg='green')))

    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)


# WORKSPACE get
# =============
@workspace.command(name='current',
                   short_help='Return name of {} workspace'.format(click.style('current', bold=True)))
@context_check
@health_check
@workspace_check
@pass_obj(WorkspaceFacade)
def current_workspace(facade: WorkspaceFacade):
    """
    Get current model environment workspace.
    """
    try:
        # return <name> as workspace
        name = facade.current()
        click.echo("{} - Workspace {} is currently set".format(
            click.style("Info", bold=True, fg='green'),
            click.style(name, bold=True, fg='green')))

    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)


def print_list(name, entries):
    click.echo('{}:\n'.format(click.style(name, bold=True, fg='green')))
    for pipeline in entries:
        click.echo(f"- {pipeline}")
    click.echo("\n")


# WORKSPACE info
# ==============
@workspace.command(name='info',
                   short_help='Identify available resources in {} workspace'.format(click.style('current', bold=True)))
@context_check
@health_check
@workspace_check
@pass_obj(WorkspaceFacade)
def workspace_info(facade: WorkspaceFacade):
    """
    Identify all running resources within a workspace.
    """
    try:

        info = facade.info()['response']

        click.echo('\n--- Workspace {} ---\n'.format(click.style(info['name'], bold=True, fg='green')))
        print_list('Pipelines', info['pipelines'])
        print_list('Repos', info['repos'])
    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)


# WORKSPACE kill
# ==============
@workspace.command(name='kill',
                   short_help='{}'.format(
                       click.style('Remove all available resources in current workspace', bold=True, fg='red')))
@context_check
@health_check
@workspace_check
@pass_obj(WorkspaceFacade)
def kill_workspace(facade: WorkspaceFacade):
    """
    Kill all resources running in a workspace.
    """

    name = facade.current()
    # confirm kill
    if not click.confirm('{} - Are you sure about killing all {} resources?'.format(
            click.style("Warning", bold=True, fg='yellow'),
            click.style(name, bold=True, fg='red')),
            abort=False):
        click.echo("{} - Workspace {} kill operation aborted. Re-initiate using `{}` if required".format(
            click.style("Info", bold=True, fg='white'),
            click.style(name, bold=True, fg='green'),
            click.style("kaos workspace kill", bold=True, fg='green')))
        sys.exit(1)
    else:
        name = facade.delete()

        click.echo('{} - Successfully killed all {} resources'.format(
            click.style("Info", bold=True, fg='green'),
            click.style(name, bold=True, fg='green')))
