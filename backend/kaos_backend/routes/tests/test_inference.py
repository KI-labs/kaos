import os

import pytest
from flask import Flask

from kaos_backend.controllers.inference import InferenceController
from kaos_backend.exceptions.exceptions import PipelineNotFoundError, PipelineInStandby
from kaos_backend.exceptions.register import register_application_exception
from kaos_backend.routes.inference import build_inference_blueprint

os.environ["TOKEN"] = "TEST"


@pytest.fixture()
def client(mocker):
    inference_controller = InferenceController(None)
    inference_blueprint = build_inference_blueprint(inference_controller)

    def side_effect(endpoint_name):
        if endpoint_name == 'existing_endpoing':
            return {"asdf": 111}
        elif endpoint_name == 'nonexistent_endpoint':
            raise PipelineNotFoundError("asdf")
        elif endpoint_name == 'standby_endpoint':
            raise PipelineInStandby("asdf")

    inference_controller.get_logs = mocker.Mock(side_effect=side_effect)

    app = Flask(__name__)
    app.register_blueprint(inference_blueprint)
    # registers handlers to Application Exception
    register_application_exception(app)

    client = app.test_client()
    yield client


def test_inference_get_logs(client):
    token = os.getenv("TOKEN")
    r = client.get("/inference/existing_endpoing/logs", headers={"Token": token})
    assert r.status_code == 200


def test_inference_get_logs_nonexistent_endpoint(client):
    token = os.getenv("TOKEN")
    r = client.get("/inference/nonexistent_endpoint/logs", headers={"Token": token})
    assert r.status_code == 404


def test_inference_get_logs_standby_endpoint(client):
    token = os.getenv("TOKEN")
    r = client.get("/inference/standby_endpoint/logs", headers={"Token": token})
    assert r.status_code == 500
