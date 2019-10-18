import logging
import os

from flask import Flask
from kaos_backend.clients.pachyderm import PachydermClient
from kaos_backend.controllers.data import DataController
from kaos_backend.controllers.inference import InferenceController
from kaos_backend.controllers.internal import InternalController
from kaos_backend.controllers.notebook import NotebookController
from kaos_backend.controllers.train import TrainController
from kaos_backend.controllers.workspace import WorkspaceController
from kaos_backend.exceptions.register import register_application_exception
from kaos_backend.routes.data import build_data_blueprint
from kaos_backend.routes.inference import build_inference_blueprint
from kaos_backend.routes.internal import build_internal_blueprint
from kaos_backend.routes.notebook import build_notebook_blueprint
from kaos_backend.routes.train import build_train_blueprint
from kaos_backend.routes.workspace import build_workspace_blueprint
from kaos_backend.services.job_service import JobService
from python_pachyderm import PfsClient, PpsClient

PACHY_HOST = os.getenv("PACHD_SERVICE_HOST", "localhost")
PACHY_PORT = os.getenv("PACHD_SERVICE_PORT_API_GRPC_PORT", 30650)

pfs_client = PfsClient(PACHY_HOST, PACHY_PORT)
pps_client = PpsClient(PACHY_HOST, PACHY_PORT)

pachyderm_client = PachydermClient(pps_client, pfs_client)
job_service = JobService(pachyderm_client)

train_blueprint = build_train_blueprint(TrainController(job_service))
inference_blueprint = build_inference_blueprint(InferenceController(job_service))
notebook_blueprint = build_notebook_blueprint(NotebookController(job_service))
workspace_blueprint = build_workspace_blueprint(WorkspaceController(job_service))
data_blueprint = build_data_blueprint(DataController(job_service))
internal_blueprint = build_internal_blueprint(InternalController(job_service))

app = Flask(__name__)

app.register_blueprint(internal_blueprint)
app.register_blueprint(inference_blueprint)
app.register_blueprint(notebook_blueprint)
app.register_blueprint(workspace_blueprint)
app.register_blueprint(data_blueprint)
app.register_blueprint(train_blueprint)

register_application_exception(app)

# setup logging
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)
