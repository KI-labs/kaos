import os

import flask
import pytest
import uuid

from kaos_backend.controllers.tests import create_job_service, t_any, create_train_zip
from kaos_backend.controllers.train import TrainController
from kaos_backend.exceptions.exceptions import InvalidBundleError
from kaos_backend.util.tests import create_zip

from kaos_model.common import TrainJobListing, SubmissionInfo


def generate_submission_info():
    return SubmissionInfo(
        job_id=uuid.uuid4().hex,
        state="aaa",
        started="aa",
        duration=1,
        hyperopt="pp",
        progress="It's ain't much, but it's honest progress"
    )


def test_list_train(mocker):
    job_service = create_job_service(mocker, workspaces=["pippo"])

    submission_info_1 = generate_submission_info()
    submission_info_2 = generate_submission_info()
    submission_info_3 = generate_submission_info()

    job_service.list_training_jobs = mocker.Mock(return_value=[submission_info_1])
    job_service.list_build_train_jobs = mocker.Mock(return_value=[submission_info_2])
    job_service.list_ingestion_jobs = mocker.Mock(return_value=[submission_info_3])

    reference_listing = TrainJobListing(training=[submission_info_1],
                                        building=[submission_info_2],
                                        ingesting=[submission_info_3])

    with flask.Flask("Test").app_context():
        train_controller = TrainController(job_service)
        print(train_controller.list_training_jobs("pippo"))
        assert train_controller.list_training_jobs("pippo") == reference_listing


def test_invalid_submit_training(mocker):

    service = create_job_service(mocker)

    with pytest.raises(InvalidBundleError, match="Bundle is malformed"):
        with flask.Flask("Test").app_context():
            controller = TrainController(service)
            controller.submit_training("test_workspace", "test_user", data_bytes=b'0x1', cpu=None, memory=None)


def test_submit_training_missing_root(mocker):

    service = create_job_service(mocker)

    data_bytes, _, temp_dir, zip_filename = create_zip()

    with pytest.raises(InvalidBundleError, match="Missing root directory in source-code bundle"):
        with flask.Flask("Test").app_context():
            controller = TrainController(service)
            controller.submit_training("test_workspace", "test_user", data_bytes=data_bytes, cpu=None, memory=None)

        temp_dir.cleanup()
        os.remove(zip_filename)


def test_submit_training(mocker):

    service = create_job_service(mocker)

    mocker.patch.object(service, 'submit_training_code')

    data_bytes, temp_dir, zip_filename = create_train_zip()

    service.submit_training_data = mocker.Mock()
    with flask.Flask("Test").app_context():
        controller = TrainController(service)
        controller.submit_training("test_workspace", "test_user", data_bytes=data_bytes, cpu=None, memory=None)
        service.submit_training_code.assert_called_with("test_workspace",
                                                        "test_user",
                                                        t_any(str),
                                                        gpu=0,
                                                        cpu=None,
                                                        memory=None)

    temp_dir.cleanup()
    os.remove(zip_filename)
