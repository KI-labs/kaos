from flask import Blueprint, request

from kaos_backend.controllers.data import DataController
from kaos_backend.util.flask import jsonify
from kaos_backend.util.validators import validate_request


def build_data_blueprint(controller: DataController):
    blueprint = Blueprint('data', __name__)

    @blueprint.route("/data/<workspace>/features", methods=["POST"])
    @jsonify
    @validate_request
    def feature_submit(workspace):
        user = request.args.get('user', 'default').replace('.', '')
        cpu = request.args.get('cpu', None)
        memory = request.args.get('memory', None)
        gpu = int(request.args.get('gpu', 0))
        return controller.put_features(workspace, user, request.files['data'].read(), cpu=cpu, memory=memory, gpu=gpu)

    @blueprint.route("/data/<workspace>/manifest", methods=["POST"])
    @jsonify
    @validate_request
    def manifest_submit(workspace):
        user = request.args.get('user', 'default').replace('.', '')
        cpu = request.args.get('cpu', None)
        memory = request.args.get('memory', None)
        gpu = int(request.args.get('gpu', 0))
        return controller.put_manifest_features(workspace, user, request.files['data'].read(), cpu=cpu, memory=memory, gpu=gpu)

    @blueprint.route("/data/<workspace>/params", methods=["POST"])
    @jsonify
    @validate_request
    def param_submit(workspace):
        user = request.args.get('user', 'default').replace('.', '')
        parallelism = int(request.args.get('parallelism', 1))
        cpu = request.args.get('cpu', None)
        memory = request.args.get('memory', None)
        gpu = int(request.args.get('gpu', 0))
        return controller.put_params(workspace, user, request.files['data'].read(),
                                     parallelism=parallelism, cpu=cpu, memory=memory, gpu=gpu)

    @blueprint.route("/data/<workspace>/notebook", methods=["POST"])
    @jsonify
    @validate_request
    def notebook_submit(workspace):
        user = request.args.get('user', 'default').replace('.', '')
        return controller.put_notebook_data(workspace, user, request.data)

    return blueprint
