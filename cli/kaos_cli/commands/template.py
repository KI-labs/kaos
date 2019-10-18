import click

from kaos_cli.exceptions.handle_exceptions import handle_specific_exception, handle_exception
from kaos_cli.facades.template_facade import TemplateFacade
from kaos_cli.utils.custom_classes import CustomHelpOrder, NotRequiredIf
from kaos_cli.utils.decorators import init_check, pass_obj
from kaos_cli.utils.rendering import render_table
from kaos_cli.utils.validators import validate_inputs


# TEMPLATE group
# ==============
@click.group(name='template', cls=CustomHelpOrder,
             short_help='Retrieves {} for getting started'.format(click.style('templates', bold=True)))
@init_check
def template():
    """
    Retrieves templates to easily getting started with kaos
    """
    pass


# TEMPLATE list
# =============
@template.command(name='list',
                  short_help='List all available templates')
@pass_obj(TemplateFacade)
def list_templates(facade: TemplateFacade):
    """
    List all available templates.
    """
    try:
        templates = facade.list()

        table = render_table(templates, include_ind=True)
        click.echo(table)

    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)


# TEMPLATE download
# =================
@template.command(name='get',
                  short_help='Get template source')
@click.option('-n', '--name', type=str, help='template name', cls=NotRequiredIf,
              not_required_if='ind')
@click.option('-i', '--ind', type=int, help='template index', cls=NotRequiredIf,
              not_required_if='name')
@pass_obj(TemplateFacade)
def get_template(facade: TemplateFacade, name, ind):
    """
    Get template.
    """
    try:

        # ensure arguments are correctly defined
        validate_inputs([name, ind], ['name', 'ind'])

        # selection by index
        if ind is not None:
            name = facade.get_template_name_by_ind(ind)

        name = facade.validate(name)

        facade.download(name)

        click.echo("{} - Successfully loaded {} template".format(
            click.style("Info", bold=True, fg='green'),
            click.style(name, bold=True, fg='green')))

    except Exception as e:
        handle_specific_exception(e)
        handle_exception(e)
