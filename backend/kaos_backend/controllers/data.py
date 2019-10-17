import hashlib
import json
import os

from flask import current_app as app

from kaos_backend.constants import MANIFEST_DIR_PREFIX
from kaos_backend.exceptions.exceptions import InvalidBundleError
from kaos_backend.services.job_service import JobService
from kaos_backend.util.helpers import product_dict, BundleDirectory, build_hash, BundleHash
from kaos_backend.util.validators import BundleValidator


class DataController:
    """
    Controller for deploying inferences atop pachyderm.
    """

    def __init__(self, job_service: JobService):
        self.job_service = job_service

    def put_features(self, workspace, user, data_bytes, cpu=None, memory=None, gpu=0):
        app.logger.debug("@%s: putting features in %s - %s", DataController.__name__, workspace, user)

        with BundleDirectory(data_bytes) as temp_dir:
            if BundleValidator.is_empty(temp_dir):
                raise InvalidBundleError("Features data directory must be non-empty")

            data_glob = os.path.basename(BundleHash.hash(temp_dir, data_bytes))

            self.job_service.define_bundle_ingestion_pipeline(workspace, user, data_glob)

            # submit data
            self.job_service.submit_training_data(workspace, user, temp_dir)

            # update pipeline with data glob pattern
            glob_name = os.listdir(temp_dir)[0]
            app.logger.debug("@%s: updating %s train pipeline for data features [/%s]",
                             DataController.__name__, workspace, glob_name)
            self.job_service.define_train_pipeline(workspace, user, data_name=glob_name,
                                                   cpu=cpu, memory=memory, gpu=gpu)

            return {'glob_name': glob_name}

    def put_manifest_features(self, workspace, user, data_bytes, cpu, memory, gpu):
        app.logger.debug("@%s: put manifest in %s - %s", DataController.__name__, workspace, user)

        # update pipeline with data glob pattern
        data_hash = hashlib.sha256(data_bytes).hexdigest()[:5]

        glob_name = f"{MANIFEST_DIR_PREFIX}:{data_hash}"

        self.job_service.define_manifest_ingestion_pipeline(workspace, user, glob_name)

        # submit data
        self.job_service.submit_manifest(workspace, user, data_bytes, glob_name)

        app.logger.debug("@%s: updating %s train pipeline for data manifest [/%s]",
                         DataController.__name__, workspace, glob_name)
        self.job_service.define_train_pipeline(workspace, user,
                                               data_name=glob_name, cpu=cpu, memory=memory, gpu=gpu)
        return {'glob_name': glob_name}

    def put_params(self, workspace, user, data_bytes, parallelism=1, cpu=None, memory=None, gpu=0):
        app.logger.debug("@%s: putting hyper-parameters in %s - %s", DataController.__name__, workspace, user)

        # create hash
        glob_name = build_hash(data_bytes)

        # format params
        param_dict = json.loads(data_bytes)
        params = list(product_dict(**param_dict))

        # write to unique directory
        self.job_service.submit_params(workspace, user, params, glob_name)

        # update pipeline with hyper glob pattern
        if params[0]:
            app.logger.debug("@%s: updating %s train pipeline for hyper-parameters [/%s/*]",
                             DataController.__name__, workspace, glob_name)
            self.job_service.define_train_pipeline(workspace, user, hyper_name=f"{glob_name}/*",
                                                   parallelism=parallelism, cpu=cpu, memory=memory, gpu=gpu)
        return {'glob_name': glob_name, 'params': params}

    def put_notebook_data(self, workspace, user, data_bytes):
        app.logger.debug("@%s: putting notebook data in %s - %s", DataController.__name__, workspace, user)

        with BundleDirectory(data_bytes) as temp_dir:
            if BundleValidator.is_empty(temp_dir):
                raise InvalidBundleError("Notebook data directory must be non-empty")

            self.job_service.submit_notebook_data(workspace, user, temp_dir)
