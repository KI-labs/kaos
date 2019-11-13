from flask import Blueprint, request, make_response

from kaos_backend.controllers.train import TrainController
from kaos_backend.util.flask import jsonify

from kaos_model.api import PagedResponse, Response

from kaos_backend.util.validators import validate_request


def build_train_blueprint(controller: TrainController):
    blueprint = Blueprint('train', __name__)

    @blueprint.route("/train/<workspace>", methods=["GET"])
    @jsonify
    @validate_request
    def train_list(workspace):
        return Response(response=controller.list_training_jobs(workspace))

    @blueprint.route("/train/<workspace>", methods=["POST"])
    @jsonify
    @validate_request
    def train_submit(workspace):
        user = request.args.get('user', 'default').replace('.', '')
        cpu = request.args.get('cpu', None)
        memory = request.args.get('memory', None)
        gpu = int(request.args.get('gpu', 0))
        return controller.submit_training(workspace, user, request.files['data'].read(), cpu=cpu, memory=memory, gpu=gpu)

    @blueprint.route("/train/<workspace>/<job_id>", methods=["GET"])
    @jsonify
    @validate_request
    def train_info(workspace, job_id):
        sort_by = request.args.get('sort_by', None)
        page_id = int(request.args.get('page_id', 0))
        job_info, page_count = controller.get_training_info(workspace, job_id, sort_by=sort_by, page_id=page_id)
        return PagedResponse(
            page_id=page_id,
            page_count=page_count,
            response=job_info
        )

    @blueprint.route("/train/<workspace>/inspect", methods=["GET"])
    @jsonify
    @validate_request
    def train_inspect(workspace):
        return controller.inspect_training_pipeline(workspace)

    @blueprint.route("/train/<workspace>/<job_id>/bundle", methods=["GET"])
    @validate_request
    def train_get(workspace, job_id):
        include_code = request.args.get('include_code', default='True', type=str) == 'True'
        include_data = request.args.get('include_data', default='False', type=str) == 'True'
        include_model = request.args.get('include_model', default='True', type=str) == 'True'
        model_id = request.args.get('model_id', default=None, type=str)
        return make_response(
            controller.get_bundle(workspace, job_id, include_code, include_data, include_model, model_id))

    @blueprint.route("/train/<workspace>/build/<job_id>/logs", methods=["GET"])
    @jsonify
    @validate_request
    def build_train_logs(workspace, job_id):
        return controller.get_build_logs(workspace, job_id)

    @blueprint.route("/train/<workspace>/<job_id>/logs", methods=["GET"])
    @jsonify
    @validate_request
    def train_logs(workspace, job_id):
        return controller.get_logs(workspace, job_id)

    @blueprint.route("/train/<workspace>/<model_id>/provenance", methods=["GET"])
    @jsonify
    @validate_request
    def train_provenance(workspace, model_id):
        return controller.get_model_provenance_dag(workspace, model_id)

    @blueprint.route("/train/<workspace>/<job_id>", methods=["DELETE"])
    @jsonify
    @validate_request
    def train_kill(workspace, job_id):
        return controller.kill_training_job(workspace, job_id)

    return blueprint
