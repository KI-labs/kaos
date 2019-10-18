from functools import partial

from kaos_cli.utils.helpers import verbose_run, run_cmd


class TerraformService:

    def __init__(self):
        self.run_cmd = run_cmd

    def set_verbose(self, verbose):
        self.run_cmd = partial(verbose_run, verbose)

    def init(self, directory):
        self.run_cmd(f"terraform init {directory} ")

    def new_workspace(self, directory, env):
        self.run_cmd(f"terraform workspace new {env} {directory}")

    def exists_workspace(self, directory, env):
        cmd = f"if [[ $(terraform workspace list {directory} | grep {env} || echo \"n\") != \"n\" ]]; then exit 1; fi"
        rc, _, _ = self.run_cmd(cmd)
        return rc > 0

    def select_workspace(self, directory, env):
        self.run_cmd(f"terraform workspace select {env} {directory}")

    def plan(self, directory, extra_vars):
        self.run_cmd(f"terraform plan --var-file={directory}/terraform.tfvars "
                     f"{extra_vars} {directory}")

    def apply(self, directory, extra_vars):
        self.run_cmd(f"terraform apply --var-file={directory}/terraform.tfvars "
                     f"{extra_vars} --auto-approve {directory}")

    def destroy(self, directory, extra_vars):
        self.run_cmd(f"terraform destroy --var-file={directory}/terraform.tfvars "
                     f"{extra_vars} --auto-approve {directory}")
