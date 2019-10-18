import click

# INIT command
# ============
from kaos_cli.facades.backend_facade import BackendFacade
from kaos_cli.utils.decorators import pass_obj


@click.command(name='init',
               short_help='Initialize the {} environment'.format(
                   click.style('kaos', bold=True)))
@click.option('-e', '--endpoint', type=str, help='endpoint associated with the kaos backend', required=True)
@click.option('-t', '--token', prompt=True, hide_input=True, help='token for accessing the kaos backend', required=True)
@click.option('-f', '--force', is_flag=True, help='overwrite current state directory')
@pass_obj(BackendFacade)
def init(backend: BackendFacade, endpoint, token, force):
    """
    Configure and connect kaos with deployed backend infrastructure.
    """

    # handle "force" STATE creation
    if force:
        click.echo("{} - Force initialization of {}".format(
            click.style("Warning", bold=True, fg='yellow'),
            click.style("kaos", bold=True)))

    elif backend.is_created():
        click.confirm('{} - {} is already initialized in this directory. Do you want to overwrite?'.format(
            click.style("Warning", bold=True, fg='yellow'),
            click.style("kaos", bold=True)), abort=True)

    backend.init(endpoint, token)

    click.echo('{} - {} successfully connected to {}'.format(
        click.style("Info", bold=True, fg='green'),
        click.style("kaos", bold=True),
        click.style(endpoint, bold=True, fg='green')))
