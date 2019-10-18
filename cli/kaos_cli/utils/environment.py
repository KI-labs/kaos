import re
import shutil
from collections import defaultdict
from distutils.version import StrictVersion

import click
from kaos_cli.exceptions.exceptions import CommandError, VersionError, SimpleApplicationError

from ..constants import MINIMAL_TF_VERSION, AWS
from ..utils.helpers import run_cmd

VERSION_REGEX = r'Terraform v\s*([\d.]+)'


def format_missing_command_error(command):
    return "{} - {} is not installed. You should install it first to run {}".format(
        click.style("Warning", bold=True, fg='yellow'),
        click.style(command, bold=True, fg='white'),
        click.style('kaos', bold=True, fg='blue'))


def check_commands(commands):
    return list(filter(lambda cmd: not shutil.which(cmd), commands))


def check_version(tool_name, version_command, min_version):
    code, out, err = run_cmd(version_command)
    version_str = re.search(VERSION_REGEX, out.decode("utf-8")).group(1)
    if version_str:
        version = StrictVersion(version_str)
        if version < min_version:
            message = f"{tool_name} version {version} is not supported. Upgrade to at least {MINIMAL_TF_VERSION}"
            raise VersionError(message)
    else:
        raise SimpleApplicationError("Could not check terraform version. Aborting")


def check_environment(cloud=None):
    commands_by_cloud = defaultdict(lambda: ["dot", "terraform", "jq", "numfmt"])
    commands_by_cloud[AWS].append("aws-iam-authenticator")

    missing_commands = check_commands(commands_by_cloud[cloud])
    if missing_commands:
        raise CommandError(missing_commands)

    check_version("Terraform", "terraform --version", MINIMAL_TF_VERSION)
