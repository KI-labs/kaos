import os

import flask
import pytest
from kaos_backend.controllers.notebook import NotebookController
from kaos_backend.controllers.tests import create_job_service, t_any, create_train_zip
from kaos_backend.exceptions.exceptions import InvalidBundleError
from kaos_backend.util.tests import create_zip


def test_invalid_submit_notebook(mocker):
    service = create_job_service(mocker)

    with pytest.raises(InvalidBundleError, match="Bundle is malformed"):
        with flask.Flask("Test").app_context():
            controller = NotebookController(service)
            controller.submit_notebook("test_workspace",
                                       "test_user",
                                       data_bytes=b'0x1')


def test_submit_notebook_missing_root(mocker):
    service = create_job_service(mocker)

    data_bytes, _, temp_dir, zip_filename = create_zip()

    with pytest.raises(InvalidBundleError, match="Missing root directory in source-code bundle"):
        with flask.Flask("Test").app_context():
            controller = NotebookController(service)
            controller.submit_notebook("test_workspace",
                                       "test_user",
                                       data_bytes=data_bytes)

        temp_dir.cleanup()
        os.remove(zip_filename)


def test_submit_notebook(mocker):
    service = create_job_service(mocker)

    mocker.patch.object(service, 'submit_notebook_code')

    data_bytes, temp_dir, zip_filename = create_train_zip()

    service.create_notebook_data = mocker.Mock()
    with flask.Flask("Test").app_context():
        controller = NotebookController(service)
        controller.submit_notebook("test_workspace",
                                   "test_user",
                                   data_bytes=data_bytes)
        service.submit_notebook_code.assert_called_with("test_workspace",
                                                        "test_user",
                                                        t_any(str),
                                                        gpu=0,
                                                        cpu=None,
                                                        memory=None)

    temp_dir.cleanup()
    os.remove(zip_filename)


def test_submit_notebook_without_data(mocker):
    service = create_job_service(mocker)

    mocker.patch.object(service, 'submit_notebook_code')

    service.create_notebook_data = mocker.Mock()
    with flask.Flask("Test").app_context():
        controller = NotebookController(service)
        controller.submit_notebook("test_workspace", "test_user")
        service.submit_notebook_code.assert_called_with("test_workspace",
                                                        "test_user",
                                                        t_any(str),
                                                        gpu=0,
                                                        cpu=None,
                                                        memory=None)
