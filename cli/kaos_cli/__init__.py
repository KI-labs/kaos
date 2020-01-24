import click
from kaos_cli.factories.simple_factory import SimpleFactory

from .commands.build import build, destroy, list_all
from .commands.initialization import init
from .commands.notebook import notebook
from .commands.serve import serve
from .commands.template import template
from .commands.train import train
from .commands.workspace import workspace
from .utils.custom_classes import CustomHelpOrder


@click.group(cls=CustomHelpOrder)
@click.pass_context
def kaos(ctx):
    """
\b
██╗  ██╗ █████╗  ██████╗ ███████╗
██║ ██╔╝██╔══██╗██╔═══██╗██╔════╝
█████╔╝ ███████║██║   ██║███████╗
██╔═██╗ ██╔══██║██║   ██║╚════██║
██║  ██╗██║  ██║╚██████╔╝███████║
╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝
\b

Open source cloud agnostic minimal DevOps private versioned ML platform.

    """

    factory = SimpleFactory()
    factory.create()
    ctx.obj = factory


kaos.add_command(build)
kaos.add_command(destroy)
kaos.add_command(init)
kaos.add_command(template)
kaos.add_command(workspace)
kaos.add_command(notebook)
kaos.add_command(train)
kaos.add_command(serve)
