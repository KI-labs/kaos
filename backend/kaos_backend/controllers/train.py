import os
import shutil
from tempfile import TemporaryDirectory

from flask import current_app as app

from kaos_backend.constants import TRAIN_PIPELINE_PREFIX
from kaos_backend.exceptions.exceptions import PageError, ModelNotFoundError, JobNotFoundError, JobNotRunningError
from kaos_backend.services.job_service import JobService
from kaos_backend.util.dag import build_model_provenance_dag
from kaos_backend.util.helpers import BundleDirectory, BundleHash, remove_files_from_directory
from kaos_backend.util.validators import BundleValidator

from kaos_model.common import DataDescriptor, TrainJobListing


class TrainController:
    """
    Controller for train jobs management in pachyderm.
    """

    PAGE_SIZE = 10

    exclude_filename = "pipeline_args.json"

    def __init__(self, job_service: JobService):
        self.job_service = job_service

    def list_training_jobs(self, workspace):
        app.logger.debug("@%s: list training in %s", TrainController.__name__, workspace)

        return TrainJobListing(
            training=self.job_service.list_training_jobs(workspace),
            building=self.job_service.list_build_train_jobs(workspace),
            ingesting=self.job_service.list_ingestion_jobs(workspace)
        )

    def inspect_training_pipeline(self, workspace):
        app.logger.debug("@%s: inspect %s training pipeline", TrainController.__name__, workspace)
        return self.job_service.inspect_training_pipeline(f"{TRAIN_PIPELINE_PREFIX}-{workspace}")

    def get_training_info(self, workspace, job_id, sort_by=None, page_id=0):
        app.logger.debug("@%s: get training job %s in %s", TrainController.__name__, job_id, workspace)

        if page_id < 0:
            return PageError("page id must be non-negative")
        job_info = self.job_service.get_training_info(workspace, job_id, extract_metric=sort_by)
        partitions = job_info.partitions
        page_count = len(partitions) // self.PAGE_SIZE + 1

        if sort_by:
            partitions.sort(key=lambda p: (p.score is None, p.score), reverse=True)

        page_start = page_id * self.PAGE_SIZE
        page_finish = page_start + self.PAGE_SIZE
        job_info.partitions = partitions[page_start:page_finish]

        return job_info, page_count

    def submit_training(self, workspace, user, data_bytes, cpu=None, memory=None, gpu=0):
        app.logger.debug("@%s: create training job %s - %s", TrainController.__name__, workspace, user)

        with BundleDirectory(data_bytes) as temp_dir:
            BundleValidator.validate_train_bundle_structure(temp_dir)

            hashed_bundle = BundleHash.hash(temp_dir, data_bytes)

            self.job_service.submit_training_code(workspace, user, temp_dir, cpu=cpu, memory=memory, gpu=gpu)

        return {'glob_name': os.path.split(hashed_bundle)[-1]}

    def get_logs(self, workspace, job_id):
        if self.job_service.check_train_job_exists(workspace, job_id):
            logs_result = self.job_service.get_train_logs(workspace, job_id)
            app.logger.debug("@%s: getting logs of training job %s in workspace %s: %s",
                             TrainController.__name__, job_id, workspace, logs_result)
            return logs_result
        elif self.job_service.check_build_train_job_exists(workspace, job_id):
            logs_result = self.job_service.get_build_train_logs(workspace, job_id)
            app.logger.debug("@%s: getting logs of build train job %s in workspace %s: %s",
                             TrainController.__name__, job_id, workspace, logs_result)
            return logs_result
        else:
            app.logger.error("@%s: could not find job %s in pipeline %s while getting logs",
                             TrainController.__name__, job_id, workspace)
            raise JobNotFoundError(job_id)

    def get_bundle(self, workspace, job_id, include_code, include_data, include_model, model_id=None):
        app.logger.debug("@%s: get bundle of training job %s on %s", TrainController.__name__, job_id, workspace)

        with TemporaryDirectory() as temp_dir:
            bundle_dir = os.path.join(temp_dir, "bundle")
            os.mkdir(bundle_dir)

            partitions = self.job_service.get_datum_by_job_id(workspace, job_id)
            is_hyper_opt = bool(partitions[0].hyperparams)

            if include_model:
                self.download_model(bundle_dir, model_id, partitions, is_hyper_opt)

            if include_code:
                self.download_code(bundle_dir, partitions[0].code)

            if include_data:
                self.download_data(bundle_dir, partitions[0].data)

            shutil.make_archive(os.path.join(temp_dir, job_id), "zip", bundle_dir)
            data_bytes = open(os.path.join(temp_dir, f"{job_id}.zip"), 'rb').read()

            return data_bytes

    def download_data(self, bundle_dir, data_descriptor):
        self.job_service.download_by_info(data_descriptor, os.path.join(bundle_dir, 'data'))

    def download_code(self, bundle_dir, code_descriptor):
        code_dir = os.path.join(bundle_dir, 'code')
        self.job_service.download_by_info(code_descriptor, code_dir)
        remove_files_from_directory(code_dir, self.exclude_filename)

    def download_model(self, bundle_dir, model_id, datums, hyper_opt):
        if model_id:
            datums = list(filter(lambda x: model_id in x.output.path, datums))
            if len(datums) == 0:
                raise ModelNotFoundError(model_id)

        for datum in datums:
            output_branch, model_prefix = datum.output.path.split(":")
            head_commit = self.job_service.get_head_commit(model_prefix, output_branch, datum.output.repo)
            model_descriptor = DataDescriptor(
                path=model_prefix,
                branch=output_branch,
                repo=datum.output.repo,
                commit=head_commit
            )
            self.job_service.download_by_info(model_descriptor,
                                              os.path.join(bundle_dir, 'models'))
            if hyper_opt:
                self.job_service.download_by_info(datum.hyperparams,
                                                  os.path.join(bundle_dir, 'models', model_prefix))

    def get_model_provenance_dag(self, workspace, model_id):
        app.logger.debug("@%s: get model %s provenance on %s", TrainController.__name__, model_id, workspace)

        model_info = self.job_service.get_model_info(workspace, model_id)
        provenance_info = self.job_service.get_model_provenance(workspace, model_info.commit_id, model_id)
        dot = build_model_provenance_dag(workspace, model_info, provenance_info)
        return dot.source

    def kill_training_job(self, workspace, job_id):
        app.logger.debug("@%s: kill training job %s in workspace %s", TrainController.__name__, job_id, workspace)

        if self.job_service.check_train_job_running(workspace, job_id):
            kill_result = self.job_service.delete_train_job(workspace, job_id)
            app.logger.debug("@%s: killed training job %s in workspace %s: %s",
                             TrainController.__name__, job_id, workspace, kill_result)
            return kill_result
        elif self.job_service.check_build_train_job_running(workspace, job_id):
            kill_result = self.job_service.delete_build_train_job(workspace, job_id)
            app.logger.debug("@%s: killed build train job %s in workspace %s: %s",
                             TrainController.__name__, job_id, workspace, kill_result)
            return kill_result
        else:
            if self.job_service.check_train_job_exists(workspace, job_id) or \
                    self.job_service.check_build_train_job_exists(workspace, job_id):
                app.logger.error("@%s: could not delete job %s in pipeline %s, it is not running",
                                 TrainController.__name__, job_id, workspace)
                raise JobNotRunningError(job_id)
            else:
                app.logger.error("@%s: could not find job %s in pipeline %s while deleting",
                                 TrainController.__name__, job_id, workspace)
                raise JobNotFoundError(job_id)
