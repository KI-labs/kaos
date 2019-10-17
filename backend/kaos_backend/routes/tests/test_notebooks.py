import pytest
from flask import Flask
from kaos_backend.controllers.notebook import NotebookController
from kaos_backend.exceptions.exceptions import NotebookAlreadyExistsError
from kaos_backend.exceptions.register import register_application_exception
from kaos_backend.routes.notebook import build_notebook_blueprint


@pytest.fixture()
def client(mocker):

    notebook_controller = NotebookController(None)
    notebook_blueprint = build_notebook_blueprint(notebook_controller)

    def side_effect(workspace, user, data, cpu=None, memory=None, gpu=0):
        if workspace == 'new_notebook':
            return {"asdf": 111}
        elif workspace == 'notebook_exists':
            raise NotebookAlreadyExistsError("asdf")

    notebook_controller.submit_notebook = mocker.Mock(side_effect=side_effect)

    app = Flask(__name__)
    app.register_blueprint(notebook_blueprint)

    register_application_exception(app)

    client = app.test_client()
    yield client


def test_new_notebook(client):
    r = client.post("/notebook/new_notebook")
    assert r.status_code == 200


def test_notebook_exists(client):
    r = client.post("/notebook/notebook_exists")
    assert r.status_code == 409
