from functools import partial

from kaos_cli.utils.helpers import verbose_run, run_cmd


class Command:

    def __init__(self):
        self.run_cmd = run_cmd
        self.history = []

    def append(self, cmd):
        self.history.append(cmd)

    def execute(self):
        self.run_cmd(";".join(self.history))
        self.clear()

    def clear(self):
        self.history = []

    def set_verbose(self, verbose):
        self.run_cmd = partial(verbose_run, verbose)


class TerraformService:

    def __init__(self, cmd):
        self.cmd = cmd

    def set_verbose(self, verbose):
        self.cmd.set_verbose(verbose)

    def init(self, directory):
        self.cmd.append(f"terraform init {directory} ")

    def new_workspace(self, directory, env):
        self.cmd.append(f"terraform workspace new {env} {directory}")

    def select_workspace(self, directory, env):
        self.cmd.append(f"terraform workspace select {env} {directory}")

    def plan(self, directory, extra_vars):
        self.cmd.append(f"terraform plan --var-file={directory}/terraform.tfvars "
                        f"{extra_vars} {directory}")

    def apply(self, directory, extra_vars):
        self.cmd.append(f"terraform apply --var-file={directory}/terraform.tfvars "
                        f"{extra_vars} --auto-approve {directory}")

    def destroy(self, directory, extra_vars):
        self.cmd.append(f"terraform destroy --var-file={directory}/terraform.tfvars "
                        f"{extra_vars} --auto-approve {directory}")

    def execute(self):
        self.cmd.execute()

    def cd_dir(self, build_dir):
        self.cmd.append(f'cd {build_dir}')
