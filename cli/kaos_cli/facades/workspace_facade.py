import json
import re
from collections import OrderedDict

import requests
from kaos_cli.constants import WORKSPACE_CACHE, BACKEND, PACHYDERM, ACTIVE, DEFAULT
from kaos_cli.exceptions.exceptions import RequestError, WorkspaceExistsError, InvalidWorkspaceError
from kaos_cli.services.state_service import StateService
from kaos_cli.utils.validators import find_similar_term, invalidate_cache, validate_cache, validate_index
from kaos_model.api import Error


class WorkspaceFacade:

    def __init__(self, state_service: StateService):
        self.state_service = state_service

    @property
    def active_context(self):
        return self.state_service.get(ACTIVE, 'environment')

    @property
    def url(self):
        return self.state_service.get_section(self.active_context, BACKEND, 'url')

    @property
    def user(self):
        return self.state_service.get(DEFAULT, 'user')

    @property
    def workspace(self):
        return self.state_service.get(PACHYDERM, 'workspace')

    def create(self, name):
        base_url = self.url
        user = self.user

        self.workspace_name_validation(name)

        name = name.lower()
        if self.exists_by_name(name):
            raise WorkspaceExistsError(name)

        # POST /workspace/<name>
        r = requests.post(f"{base_url}/workspace/{name}", params={"user": user})

        if r.status_code < 300:
            # set workspace to state
            self.state_service.set(PACHYDERM, workspace=name)
            self.state_service.write()

            return r.json()
        elif 400 <= r.status_code < 500:
            err = Error.from_dict(r.json())
            raise RequestError(err.message)
        else:
            raise RequestError(r.text)

    def info(self):
        base_url = self.url
        name = self.workspace

        # GET /workspace/<name>
        r = requests.get(f"{base_url}/workspace/{name}")

        if r.status_code < 300:
            return r.json()
        elif 400 <= r.status_code < 500:
            err = Error.from_dict(r.json())
            raise RequestError(err.message)
        else:
            raise RequestError(r.text)

    def delete(self):
        base_url = self.url
        name = self.workspace

        # DELETE /workspace/<name>
        r = requests.delete(f"{base_url}/workspace/{name}")
        if r.status_code >= 300:
            raise RequestError(r.text)

        # unset workspace (since killed)
        name = ""
        self.state_service.set(PACHYDERM, workspace=name)
        self.state_service.write()

        # invalidate workspace cache
        invalidate_cache(WORKSPACE_CACHE, workspace=True)
        return name

    def list(self, as_dict=True):
        base_url = self.url

        # GET /workspace
        r = requests.get(f"{base_url}/workspace")
        if r.status_code >= 300:
            raise RequestError(r.text)

        data = r.json()
        if as_dict:
            data = [{"name": v} for v in data['names']]

        return data

    def current(self):
        return self.workspace

    def exists_by_name(self, name):
        workspaces = self.list(as_dict=False)['names']
        return name in workspaces

    def set_by_name(self, name):
        name = name.lower()
        self.state_service.set(PACHYDERM, workspace=name)
        self.state_service.write()

    @staticmethod
    def get_workspace_by_ind(ind):
        data = validate_cache(WORKSPACE_CACHE, command='workspace')
        loc = validate_index(len(data), ind, command='workspace')
        return data[loc]['name']

    def find_similar_workspaces(self, name):
        workspaces = self.list(as_dict=False)['names']
        return find_similar_term(name, workspaces)

    @staticmethod
    def cache(workspaces):
        with open(WORKSPACE_CACHE, 'w') as fp:
            json.dump(workspaces, fp)

    @staticmethod
    def workspace_name_validation(name):
        if not name:
            raise InvalidWorkspaceError("Invalid workspace name!")

        # check special character in name
        if not re.match(r"^[a-zA-Z0-9_]*$", name):
            raise InvalidWorkspaceError("Invalid Workspace name")
