import pytest
from flask import Flask
import os

from kaos_backend.routes.train import build_train_blueprint
from kaos_backend.controllers.train import TrainController
from kaos_backend.exceptions.exceptions import JobNotFoundError, MetricNotFound, IncompleteDatumError
from kaos_backend.exceptions.register import register_application_exception

os.environ["TOKEN"] = "TEST"


@pytest.fixture()
def client(mocker):
    train_controller = TrainController(None)
    train_blueprint = build_train_blueprint(train_controller)

    def side_effect(workspace, job_id, sort_by, page_id):
        if job_id == 'existing_job':
            return {"asdf": 111}, 1
        elif job_id == 'nonexistent_job':
            raise JobNotFoundError("asdf")
        elif job_id == 'job_no_metric':
            raise MetricNotFound("asdf")
        elif job_id == 'incomplete_datum':
            raise IncompleteDatumError("asdf")

    train_controller.get_training_info = mocker.Mock(side_effect=side_effect)

    app = Flask(__name__)
    app.register_blueprint(train_blueprint)
    # registers handlers to Application Exception
    register_application_exception(app)

    client = app.test_client()
    yield client


def test_train_info_existing_job(client):
    token = os.getenv("TOKEN")
    r = client.get("/train/asdf/existing_job", headers={"Token": token})
    assert r.status_code == 200


def test_train_info_no_job(client):
    token = os.getenv("TOKEN")
    r = client.get("/train/asdf/nonexistent_job", headers={"Token": token})
    assert r.status_code == 404


def test_train_info_no_metric(client):
    token = os.getenv("TOKEN")
    r = client.get("/train/asdf/job_no_metric", headers={"Token": token})
    assert r.status_code == 404


def test_train_info_incomplete_datum(client):
    token = os.getenv("TOKEN")
    r = client.get("/train/asdf/incomplete_datum", headers={"Token": token})
    assert r.status_code == 500
