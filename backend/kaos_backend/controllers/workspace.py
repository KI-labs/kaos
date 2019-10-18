from flask import current_app as app

from kaos_backend.services.job_service import JobService


class WorkspaceController:
    """
    Controller for train jobs management in pachyderm.
    """
    __name__ = "WorkspaceController"

    def __init__(self, job_service: JobService):
        self.job_service = job_service

    def create_workspace(self, workspace, user):
        app.logger.debug("@%s: create workspace %s on %s", WorkspaceController.__name__, workspace, user)

        app.logger.debug("@%s: initializing repositories on %s", WorkspaceController.__name__, workspace)
        self.job_service.init_workspace_repos(workspace, user)

        app.logger.debug("@%s: adding DUMMY notebook-data on %s", WorkspaceController.__name__, workspace)
        self.job_service.init_notebook_data(workspace, user)

        app.logger.debug("@%s: creating build pipeline on %s", WorkspaceController.__name__, workspace)
        build_train_resp = self.job_service.define_build_train_pipeline(workspace, user)

        app.logger.debug("@%s: creating build serve pipeline on %s", WorkspaceController.__name__, workspace)
        build_serve_resp = self.job_service.define_build_serve_pipeline(workspace, user)

        app.logger.debug("@%s: creating build notebook pipeline on %s", WorkspaceController.__name__, workspace)
        build_notebook_resp = self.job_service.define_build_notebook_pipeline(workspace, user)

        return {
            "build_train": build_train_resp,
            "build_serve": build_serve_resp,
            "build_notebook": build_notebook_resp
        }

    def describe_workspace(self, workspace):
        app.logger.debug("@%s: describe workspace on %s", WorkspaceController.__name__, workspace)

        return self.job_service.get_workspace(workspace)

    def list_workspaces(self):
        app.logger.debug("@%s: list workspaces", WorkspaceController.__name__)

        return self.job_service.list_workspaces()

    def kill_workspace(self, workspace):
        app.logger.debug("@%s: kill workspace %s", WorkspaceController.__name__, workspace)

        self.job_service.kill_workspace(workspace)
