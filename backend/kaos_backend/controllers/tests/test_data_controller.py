import hashlib
import json
import os

import flask
import pytest
from kaos_backend.controllers.data import DataController
from kaos_backend.controllers.tests import t_any, create_job_service
from kaos_backend.exceptions.exceptions import InvalidBundleError
from kaos_backend.util.helpers import build_hash
from kaos_backend.util.tests import create_zip


def test_invalid_put_features(mocker):
    service = create_job_service(mocker)

    mocker.patch.object(service, 'submit_training_data')

    controller = DataController(service)

    with pytest.raises(InvalidBundleError, match="Bundle is malformed"):
        with flask.Flask("Test").app_context():
            controller.put_features("test_workspace", "test_user", data_bytes=b'0x1')


def test_put_features(mocker):
    service = create_job_service(mocker)

    mocker.patch.object(service, 'submit_training_data')
    mocker.patch.object(service, 'define_train_pipeline')
    mocker.patch.object(service, 'define_bundle_ingestion_pipeline')

    controller = DataController(service)

    data_bytes, temp_file, temp_dir, zip_filename = create_zip()
    hash_hex = build_hash(data_bytes)
    data_name = f"{os.path.split(temp_file.name)[-1]}:{hash_hex}"

    with flask.Flask("Test").app_context():
        controller.put_features("test_workspace", "test_user", data_bytes=data_bytes)
        service.submit_training_data.assert_called_with("test_workspace", "test_user", t_any(str))
        service.define_train_pipeline.assert_called_with("test_workspace", "test_user",
                                                         data_name=data_name, cpu=None, memory=None, gpu=0)

    temp_dir.cleanup()
    os.remove(zip_filename)


def test_invalid_put_notebook_data(mocker):
    service = create_job_service(mocker)

    controller = DataController(service)

    with pytest.raises(InvalidBundleError, match="Bundle is malformed"):
        with flask.Flask("Test").app_context():
            controller.put_notebook_data("test_workspace", "test_user", data_bytes=b'0x1')


def test_put_notebook_data(mocker):
    service = create_job_service(mocker)

    mocker.patch.object(service, 'submit_notebook_data')

    controller = DataController(service)

    data_bytes, _, temp_dir, zip_filename = create_zip()

    with flask.Flask("Test").app_context():
        controller.put_notebook_data("test_workspace", "test_user", data_bytes=data_bytes)
        service.submit_notebook_data.assert_called_with("test_workspace", "test_user", t_any(str))

    temp_dir.cleanup()
    os.remove(zip_filename)


# def test_invalid_put_manifest_features(mocker):
#     service = create_job_service(mocker)
#
#     mocker.patch.object(service, 'submit_manifest')
#     mocker.patch.object(service, 'define_train_pipeline')
#     mocker.patch.object(service, 'define_manifest_ingestion_pipeline')
#
#     controller = DataController(service)
#
#     with pytest.raises(InvalidBundleError, match="Bundle is malformed"):
#         with flask.Flask("Test").app_context():
#             controller.put_manifest_features("test_workspace", "test_user",
#                                              data_bytes=b'0x1', cpu=None, memory=None, gpu=None)


def test_put_manifest_features(mocker):
    service = create_job_service(mocker)

    mocker.patch.object(service, 'submit_manifest')
    mocker.patch.object(service, 'define_train_pipeline')
    mocker.patch.object(service, 'define_manifest_ingestion_pipeline')

    controller = DataController(service)

    data_bytes = json.dumps({'path': 'a', 'url': 'b'}).encode('utf-8')
    hash_hex = hashlib.sha256(data_bytes).hexdigest()[:5]
    data_name = f"manifest:{hash_hex}"

    with flask.Flask("Test").app_context():
        controller.put_manifest_features("test_workspace", "test_user",
                                         data_bytes=data_bytes, cpu=None, gpu=0, memory=None)
        service.submit_manifest.assert_called_with("test_workspace", "test_user", t_any(bytes), data_name)
        service.define_train_pipeline.assert_called_with("test_workspace", "test_user",
                                                         data_name=data_name, cpu=None, gpu=0, memory=None)
