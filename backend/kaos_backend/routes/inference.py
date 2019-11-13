import flask
from flask import Blueprint, request, make_response

from kaos_backend.controllers.inference import InferenceController
from kaos_backend.util.flask import jsonify

from kaos_model.api import Response

from kaos_backend.util.validators import validate_request


def build_inference_blueprint(controller: InferenceController):
    blueprint = Blueprint('inference', __name__)

    @blueprint.route("/inference/<workspace>", methods=["GET"])
    @jsonify
    @validate_request
    def inference_list(workspace):
        return Response(
            response=controller.list_endpoints(workspace)
        )

    @blueprint.route("/inference/<workspace>/<model_id>", methods=["POST"])
    @jsonify
    @validate_request
    def inference_deploy(workspace, model_id):
        user = request.args.get('user', 'default').replace('.', '')
        model_id = None if model_id == "None" else model_id
        cpu = request.args.get('cpu', None)
        memory = request.args.get('memory', None)
        gpu = int(request.args.get('gpu', 0))
        return controller.deploy_inference_endpoint(workspace, user, model_id, request.files['data'].read(),
                                                    cpu=cpu, memory=memory, gpu=gpu)

    @blueprint.route("/inference/<workspace>/<endpoint_name>/bundle", methods=["GET"])
    @validate_request
    def inference_get(workspace, endpoint_name):
        return make_response(controller.get_bundle(workspace, endpoint_name))

    @blueprint.route("/inference/<workspace>/<endpoint_name>/provenance", methods=["GET"])
    @jsonify
    @validate_request
    def inference_provenance(workspace, endpoint_name):
        return controller.get_endpoint_provenance_dag(workspace, endpoint_name)

    @blueprint.route("/inference/<workspace>/build/<job_id>/logs", methods=["GET"])
    @validate_request
    def build_inference_logs(workspace, job_id):
        return flask.jsonify(controller.get_build_logs(workspace, job_id))

    @blueprint.route("/inference/<endpoint_name>/logs", methods=["GET"])
    @validate_request
    def inference_logs(endpoint_name):
        return flask.jsonify(controller.get_logs(endpoint_name))

    @blueprint.route("/inference/<endpoint_name>", methods=["DELETE"])
    @jsonify
    @validate_request
    def inference_remove(endpoint_name):
        return controller.kill_endpoint(endpoint_name)

    return blueprint
