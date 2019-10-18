from flask import current_app as app

from ..services.job_service import JobService


class InternalController(object):

    def __init__(self, job_service: JobService):
        self.job_service = job_service

    def destroy_resources(self):
        app.logger.debug("@%s: destroying all resources", InternalController.__name__)
        for workspace in self.job_service.list_workspaces()["names"]:
            app.logger.debug("@%s: killing workspace -> %s", InternalController.__name__, workspace)
            self.job_service.kill_workspace(workspace)
        self.job_service.destroy_pachyderm_resources()

    def create_training_pipeline(self, workspace, user, registry, image_name, **kwargs):
        return self.job_service.define_train_pipeline(workspace, user, registry, image_name, **kwargs)

    def create_inference_pipeline(self, workspace, user, registry, image_name, **kwargs):
        return self.job_service.deploy_inference(workspace, user, registry, image_name, **kwargs)

    def create_notebook_pipeline(self, workspace, user, registry, image_name, **kwargs):
        return self.job_service.define_notebook_pipeline(workspace, user, registry, image_name, **kwargs)
