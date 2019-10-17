import os

import flask
import pytest
from kaos_backend.controllers.inference import InferenceController
from kaos_backend.controllers.tests import create_job_service, create_inference_zip, t_any
from kaos_backend.exceptions.exceptions import InvalidBundleError
from kaos_backend.util.tests import create_zip


def test_invalid_deploy_inference_endpoint(mocker):
    service = create_job_service(mocker)

    with pytest.raises(InvalidBundleError, match="Bundle is malformed"):
        with flask.Flask("Test").app_context():
            controller = InferenceController(service)
            controller.deploy_inference_endpoint("test_workspace",
                                                 "test_user",
                                                 "test_model_id",
                                                 data_bytes=b'0x1')


def test_deploy_inference_endpoint_missing_dockerfile(mocker):
    service = create_job_service(mocker)

    data_bytes, _, temp_dir, zip_filename = create_zip()

    with pytest.raises(InvalidBundleError, match="Missing root directory in source-code bundle"):
        with flask.Flask("Test").app_context():
            controller = InferenceController(service)
            controller.deploy_inference_endpoint("test_workspace",
                                                 "test_user",
                                                 "test_model_id",
                                                 data_bytes=data_bytes)
        temp_dir.cleanup()
        os.remove(zip_filename)


def test_deploy_inference_endpoint(mocker):
    service = create_job_service(mocker)

    mocker.patch.object(service, 'build_inference_with_model_id')

    data_bytes, temp_dir, zip_filename = create_inference_zip()

    service.submit_training_data = mocker.Mock()
    with flask.Flask("Test").app_context():
        controller = InferenceController(service)
        controller.deploy_inference_endpoint("test_workspace",
                                             "test_user",
                                             "test_model_id",
                                             data_bytes=data_bytes)

        service.build_inference_with_model_id.assert_called_with("test_workspace",
                                                                 "test_user",
                                                                 "test_model_id",
                                                                 t_any(str),
                                                                 gpu=0,
                                                                 cpu=None,
                                                                 memory=None)

    temp_dir.cleanup()
    os.remove(zip_filename)
