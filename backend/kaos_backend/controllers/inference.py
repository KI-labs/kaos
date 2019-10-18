import os
import shutil
from tempfile import TemporaryDirectory

from flask import current_app as app

from kaos_backend.services.job_service import JobService
from kaos_backend.util.dag import build_full_provenance_dag
from kaos_backend.util.helpers import BundleDirectory, BundleHash, remove_files_from_directory
from kaos_backend.util.validators import BundleValidator


class InferenceController:
    """
    Controller for deploying inferences atop pachyderm.
    """

    exclude_filename = "pipeline_args.json"

    def __init__(self, job_service: JobService):
        self.job_service = job_service

    def deploy_inference_endpoint(self, workspace, user, model_id, data_bytes, cpu=None, memory=None, gpu=0):
        app.logger.debug("@%s: deploying inference endpoint in %s - %s with id %s",
                         InferenceController.__name__, workspace, user, model_id)

        with BundleDirectory(data_bytes) as temp_dir:
            BundleValidator.validate_inference_bundle_structure(temp_dir)

            hashed_bundle = BundleHash.hash(temp_dir, data_bytes)

            self.job_service.build_inference_with_model_id(workspace, user, model_id, temp_dir,
                                                           cpu=cpu, memory=memory, gpu=gpu)

        return {'glob_name': os.path.split(hashed_bundle)[-1]}

    def list_endpoints(self, workspace):
        app.logger.debug("@%s: list inference endpoint in %s", InferenceController.__name__, workspace)

        return {
            "endpoints": self.job_service.list_endpoints(workspace),
            "building": self.job_service.list_building_endpoints(workspace)
        }

    def describe_endpoint(self, workspace, pipeline_name):
        app.logger.debug("@%s: describe inference endpoint %s", InferenceController.__name__, pipeline_name)

        return self.job_service.get_service_pipeline_info(workspace, pipeline_name)

    def get_endpoint_provenance_dag(self, workspace, pipeline_name):
        app.logger.debug("@%s: get endpoint %s provenance dag in %s", InferenceController.__name__, pipeline_name,
                         workspace)

        pipeline_info = self.job_service.get_service_pipeline_info(workspace, pipeline_name, provenance=True)
        model_provenance = self.job_service.get_model_provenance(workspace,
                                                                 pipeline_info.model.commit_id,
                                                                 pipeline_info.model.model_id)

        dot = build_full_provenance_dag(workspace,
                                        pipeline_info,
                                        model_provenance)
        return dot.source

    def kill_endpoint(self, endpoint_name):
        app.logger.debug("@%s: kill endpoint %s", InferenceController.__name__, endpoint_name)

        self.job_service.delete_endpoint(endpoint_name)

    def get_logs(self, endpoint_name):
        app.logger.debug("@%s: get inference logs %s", InferenceController.__name__, endpoint_name)
        return self.job_service.get_serve_logs(endpoint_name)

    def get_build_logs(self, workspace, job_id):
        app.logger.debug("@%s: get build inference logs for job %s in workspace %s",
                         InferenceController.__name__, job_id, workspace)
        return self.job_service.get_build_serve_logs(workspace, job_id)

    def get_bundle(self, workspace, pipeline_name):
        app.logger.debug("@%s: get inference %s bundle in %s", InferenceController.__name__, pipeline_name, workspace)

        with TemporaryDirectory() as temp_dir:
            bundle_dir = os.path.join(temp_dir, "bundle")
            os.mkdir(bundle_dir)

            self.job_service.download_serve_code(workspace, pipeline_name, bundle_dir)
            remove_files_from_directory(bundle_dir, self.exclude_filename)

            shutil.make_archive(os.path.join(temp_dir, "serve_bundle"), "zip", bundle_dir)

            with open(os.path.join(temp_dir, "serve_bundle.zip"), 'rb') as f:
                return f.read()
