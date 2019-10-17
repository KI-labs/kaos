from flask import Blueprint, request

from kaos_backend.controllers.workspace import WorkspaceController
from kaos_backend.util.flask import jsonify

from kaos_model.api import Response


def build_workspace_blueprint(controller: WorkspaceController):
    blueprint = Blueprint('workspace', __name__)

    @blueprint.route("/workspace", methods=["GET"])
    @jsonify
    def list_workspace():
        return controller.list_workspaces()

    @blueprint.route("/workspace/<workspace>", methods=["POST"])
    @jsonify
    def create_workspace(workspace):
        # TODO: check through controller.check_workspace_available
        user = request.args.get('user', 'default').replace('.', '')
        return controller.create_workspace(workspace.lower(), user)

    @blueprint.route("/workspace/<workspace>", methods=["GET"])
    @jsonify
    def describe_workspace(workspace):
        return Response(
            response=controller.describe_workspace(workspace)
        )

    @blueprint.route("/workspace/<workspace>", methods=["DELETE"])
    @jsonify
    def kill_workspace(workspace):
        return controller.kill_workspace(workspace)

    return blueprint
