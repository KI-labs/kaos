import json
import os

import requests
from kaos_cli.constants import BACKEND, PACHYDERM, SERVE_CACHE, ACTIVE, DEFAULT
from kaos_cli.exceptions.exceptions import NoServingJobsError, RequestError
from kaos_cli.services.state_service import StateService
from kaos_cli.utils.helpers import build_dir, upload_with_progress_bar
from kaos_cli.utils.validators import validate_index, validate_cache, invalidate_cache
from kaos_model.api import Response, Error


class ServeFacade:

    def __init__(self, state: StateService):
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

        # GET /inference/<name>
        r = requests.get(f"{base_url}/inference/{name}", headers={"Token": self.token})
        if r.status_code >= 300:
            raise NoServingJobsError()
        return Response.from_dict(r.json()).response

    def upload_source_bundle(self, c, model_id, **kwargs):
        base_url = self.url
        name = self.workspace
        user = self.user

        kwargs['user'] = user
        with open(c, 'rb') as data:
            r = upload_with_progress_bar(data, f"{base_url}/inference/{name}/{model_id}", kwargs,
                                         "  Uploading source bundle", self.token)

        if r.status_code < 300:
            return r.json()
        elif 400 <= r.status_code < 500:
            err = Error.from_dict(r.json())
            raise RequestError(err.message)
        else:
            raise RequestError(r.text)

    def provenance(self, out_dir, endpoint):
        base_url = self.url
        name = self.workspace

        # build output directory (default = workspace)
        prov_dir = build_dir(out_dir, name, 'provenance')

        # GET /inference/<name>/<endpoint>/provenance
        r = requests.get(f"{base_url}/inference/{name}/{endpoint}/provenance", headers={"Token": self.token})

        if r.status_code < 300:
            out_fid = os.path.join(prov_dir, f"{endpoint}")
            return out_fid, r.json()
        elif 400 <= r.status_code < 500:
            err = Error.from_dict(r.json())
            raise RequestError(err.message)
        else:
            raise RequestError(r.text)

    def get_bundle(self, endpoint):
        base_url = self.url
        name = self.workspace

        # GET /inference/<name>/<endpoint>/bundle
        r = requests.get(f"{base_url}/inference/{name}/{endpoint}/bundle", headers={"Token": self.token})
        if r.status_code >= 300:
            raise RequestError(r.text)
        return name, r.content

    def get_serve_logs(self, endpoint):
        base_url = self.url

        # GET /inference/<endpoint>/logs
        r = requests.get(f"{base_url}/inference/{endpoint}/logs", headers={"Token": self.token})

        if r.status_code < 300:
            return r.json()
        elif 400 <= r.status_code < 500:
            err = Error.from_dict(r.json())
            raise RequestError(err.message)
        else:
            raise RequestError(r.text)

    def write_serve_logs(self, endpoint, logs, out_dir):
        name = self.workspace

        log_dir = build_dir(out_dir, name, 'logs')

        # save to file
        with open(os.path.join(log_dir, f"{endpoint}.log"), 'w') as dst:
            dst.write(logs)

    def get_build_logs(self, job_id):
        base_url = self.url
        name = self.workspace

        # GET /train/<name>/<job_id>/logs
        r = requests.get(f"{base_url}/inference/{name}/build/{job_id}/logs", headers={"Token": self.token})

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

        with open(os.path.join(log_dir, f"build-serve-{job_id}.log"), 'w') as dst:
            dst.write(logs)

    def delete(self, endpoint):
        base_url = self.url
        # DELETE /inference/<endpoint>
        r = requests.delete(f"{base_url}/inference/{endpoint}", headers={"Token": self.token})

        # invalidate notebook cache
        invalidate_cache(SERVE_CACHE)

        if r.status_code < 300:
            return r.json()
        elif 400 <= r.status_code < 500:
            err = Error.from_dict(r.json())
            raise RequestError(err.message)
        else:
            raise RequestError(r.text)

    @staticmethod
    def cache(running_jobs):
        # dump to "cache"
        with open(SERVE_CACHE, 'w') as fp:
            json.dump(running_jobs, fp)

    @staticmethod
    def get_endpoint_by_ind(ind):
        data = validate_cache(SERVE_CACHE, command='serve')
        loc = validate_index(len(data), ind, command='serve')
        return data[loc]['name']
