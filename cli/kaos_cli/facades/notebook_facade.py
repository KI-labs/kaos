import json
import os

import requests
from kaos_cli.constants import BACKEND, PACHYDERM, NOTEBOOK_CACHE, ACTIVE, DEFAULT
from kaos_cli.exceptions.exceptions import NoNotebookError, RequestError
from kaos_cli.utils.helpers import build_dir
from kaos_cli.utils.validators import invalidate_cache, validate_cache, validate_index
from kaos_model.api import Response, Error


class NotebookFacade:

    def __init__(self, state):
        self.state_service = state

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

    @property
    def token(self):
        return self.state_service.get_section(self.active_context, BACKEND, 'token')

    def list(self):
        base_url = self.url
        name = self.workspace

        # GET /notebook/<name>
        r = requests.get(f"{base_url}/notebook/{name}", headers={"Authorization": f"Bearer {self.token}"})
        if r.status_code >= 300:
            raise NoNotebookError()

        data = r.json()
        return Response.from_dict(data).response

    def upload_data_bundle(self, c, **kwargs):
        base_url = self.url
        name = self.workspace
        user = self.user

        kwargs['user'] = user

        r = requests.post(f"{base_url}/data/{name}/notebook", data=open(c, 'rb').read(), params=kwargs,
                          headers={"Authorization": f"Bearer {self.token}"})

        if r.status_code >= 300:
            raise RequestError(f"Error while uploading data bundle: {r.text}")
        return r.json()

    def upload_source_bundle(self, c, **kwargs):
        base_url = self.url
        name = self.workspace
        user = self.user

        kwargs['user'] = user

        r = requests.post(f"{base_url}/notebook/{name}", data=open(c, 'rb').read(), params=kwargs,
                          headers={"Authorization": f"Bearer {self.token}"})

        if r.status_code >= 300:
            raise RequestError(f"Error while uploading source bundle: {r.text}")
        return r.json()

    def deploy(self, **kwargs):
        base_url = self.url
        name = self.workspace
        user = self.user

        kwargs['user'] = user
        r = requests.post(f"{base_url}/notebook/{name}", params=kwargs,
                          headers={"Authorization": f"Bearer {self.token}"})

        if r.status_code >= 300:
            raise RequestError(f"Error while deploying notebook: {r.text}")

    def get_build_logs(self, job_id):
        base_url = self.url
        name = self.workspace

        # GET /notebook/<name>/build/<job_id>/logs
        r = requests.get(f"{base_url}/notebook/{name}/build/{job_id}/logs",
                         headers={"Authorization": f"Bearer {self.token}"})
        if r.status_code < 300:
            return r.json()
        elif 400 <= r.status_code < 500:
            err = Error.from_dict(r.json())
            raise RequestError(err.message)
        else:
            raise RequestError(r.text)

    def write_build_logs(self, job_id, logs, out_dir):
        name = self.workspace

        log_dir = build_dir(out_dir, name, 'logs')

        # save to file
        with open(os.path.join(log_dir, f"build-notebook-{job_id}.log"), 'w') as dst:
            dst.write(logs)

    def delete(self, name):
        base_url = self.url

        # DELETE /notebook/<name>/<notebook>
        r = requests.delete(f"{base_url}/notebook/{name}", headers={"Authorization": f"Bearer {self.token}"})

        if r.status_code >= 300:
            raise RequestError(r.text)

        # invalidate workspace cache
        invalidate_cache(NOTEBOOK_CACHE, workspace=True)

    @staticmethod
    def get_notebook_by_ind(ind):
        data = validate_cache(NOTEBOOK_CACHE, command='notebook')
        loc = validate_index(len(data), ind, command='notebook')
        return data[loc]['name']

    @staticmethod
    def cache(running_jobs):
        # dump to "cache"
        with open(NOTEBOOK_CACHE, 'w') as fp:
            json.dump(running_jobs, fp)
