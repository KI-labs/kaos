from kaos_cli.facades.backend_facade import BackendFacade
from kaos_cli.facades.notebook_facade import NotebookFacade
from kaos_cli.facades.serve_facade import ServeFacade
from kaos_cli.facades.template_facade import TemplateFacade
from kaos_cli.facades.train_facade import TrainFacade
from kaos_cli.facades.workspace_facade import WorkspaceFacade
from kaos_cli.services.state_service import StateService
from kaos_cli.services.terraform_service import TerraformService


class SimpleFactory:

    def __init__(self):
        self.facades = None
        self.services = None

    def create(self, cloud_env):
        self.services = self._create_services()
        self.facades = self._create_facades(cloud_env, **self.services)

    def __getitem__(self, name):
        if name in self.facades:
            return self.facades.get(name)
        if name in self.services:
            return self.services.get(name)

    @staticmethod
    def _create_services():
        state_service = StateService()
        terraform_service = TerraformService()
        services = {
            'state': state_service,
            'terraform': terraform_service
        }
        return services

    @staticmethod
    def _create_facades(cloud_env, state=None, terraform=None):
        template = TemplateFacade()
        backend = BackendFacade(cloud_env, state, terraform)
        workspace = WorkspaceFacade(state)
        train = TrainFacade(state)
        serve = ServeFacade(state)
        notebook = NotebookFacade(state)

        facades = {
            BackendFacade: backend,
            WorkspaceFacade: workspace,
            TemplateFacade: template,
            TrainFacade: train,
            ServeFacade: serve,
            NotebookFacade: notebook
        }
        return facades
