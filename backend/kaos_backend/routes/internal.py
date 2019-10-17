from flask import Blueprint, request
from kaos_backend.controllers.internal import InternalController

from ..util.flask import jsonify


def build_internal_blueprint(controller: InternalController):
    blueprint = Blueprint('internal', __name__)

    @blueprint.route("/internal/resources", methods=["DELETE"])
    @jsonify
    def destroy_resources():
        return controller.destroy_resources()

    @blueprint.route("/internal/train_pipeline/<workspace>/<user>", methods=["POST"])
    @jsonify
    def upsert_training_pipeline(workspace, user):
        registry = request.args.get('registry')
        image_name = request.args.get('image_name')
        kwargs = request.get_json()
        return controller.create_training_pipeline(workspace, user, registry, image_name, **kwargs)

    @blueprint.route("/internal/notebook_pipeline/<workspace>/<user>", methods=["POST"])
    @jsonify
    def upsert_notebook_pipeline(workspace, user):
        registry = request.args.get('registry')
        image_name = request.args.get('image_name')
        kwargs = request.get_json()
        return controller.create_notebook_pipeline(workspace, user, registry, image_name, **kwargs)

    @blueprint.route("/internal/serve_pipeline/<workspace>/<user>", methods=["POST"])
    @jsonify
    def create_serve_pipeline(workspace, user):
        registry = request.args.get('registry')
        image_name = request.args.get('image_name')
        kwargs = request.get_json()
        return controller.create_inference_pipeline(workspace, user, registry, image_name, **kwargs)

    return blueprint
