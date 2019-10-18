import os

from flask import current_app as app

from kaos_backend.services.job_service import JobService
from kaos_backend.util.helpers import BundleHash, NotebookDirectory, TemporaryZipDirectory
from kaos_backend.util.validators import BundleValidator


class NotebookController:
    """
    Controller for deploying notebook services in pachyderm.
    """

    def __init__(self, client: JobService):
        self.job_service = client

    def list_notebooks(self, workspace):
        app.logger.debug("@%s: list notebooks in %s", NotebookController.__name__, workspace)

        return {
            "notebooks": self.job_service.list_notebooks(workspace),
            "building": self.job_service.list_building_notebooks(workspace)
        }

    def submit_notebook(self, workspace, user, data_bytes=None, cpu=None, memory=None, gpu=0):
        app.logger.debug("@%s: create notebook in %s - %s", NotebookController.__name__, workspace, user)
        app.logger.debug("@%s: number of gpu %s", NotebookController.__name__, gpu)

        with NotebookDirectory(data_bytes, gpu=gpu) as temp_dir:
            BundleValidator.validate_notebook_bundle_structure(temp_dir)

            if data_bytes:
                hashed_bundle = BundleHash.hash(temp_dir, data_bytes)
            else:
                # this is a workaround since we don't have data_bytes
                with TemporaryZipDirectory(temp_dir) as data_bytes:
                    hashed_bundle = BundleHash.hash(temp_dir, data_bytes)

            self.job_service.submit_notebook_code(workspace, user, temp_dir, cpu=cpu, memory=memory, gpu=gpu)

        return {'glob_name': os.path.split(hashed_bundle)[-1]}

    def get_build_logs(self, workspace, job_id):
        app.logger.debug("@%s: get logs build notebook job %s on %s", NotebookController.__name__, job_id, workspace)
        return self.job_service.get_build_notebook_logs(workspace, job_id)

    def remove_notebook(self, notebook_name):
        app.logger.debug("@%s: remove notebook %s", NotebookController.__name__, notebook_name)

        self.job_service.delete_endpoint(notebook_name)
