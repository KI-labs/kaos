import json
import os

import requests
from kaos_cli.constants import PACHYDERM, BACKEND, TRAIN_CACHE, ACTIVE, DEFAULT
from kaos_cli.exceptions.exceptions import RequestError
from kaos_cli.utils.helpers import build_dir, upload_with_progress_bar
from kaos_cli.utils.validators import validate_cache, validate_index
from kaos_model.api import Error


class TrainFacade:
    def __init__(self, state_service):
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

    @property
    def token(self):
        return self.state_service.get(BACKEND, 'token')

    def list(self):
        base_url = self.url
        name = self.workspace

        # GET /train/<name>
        r = requests.get(f"{base_url}/train/{name}", headers={"Token": self.token})
        if r.status_code < 300:
            return r.json()
        elif 400 <= r.status_code < 500:
            err = Error.from_dict(r.json())
            raise RequestError(err.message)
        else:
            raise RequestError(r.text)

    def info(self, job_id, sort_by, page_id):
        base_url = self.url
        name = self.workspace

        # GET /train/<name>/<job_id>
        r = requests.get(f"{base_url}/train/{name}/{job_id}", params={'sort_by': sort_by, 'page_id': page_id},
                         headers={"Token": self.token})

        if r.status_code < 300:
            return r.json()
        elif 400 <= r.status_code < 500:
            err = Error.from_dict(r.json())
            raise RequestError(err.message)
        else:
            err = Error.from_dict(r.json())
            if err.error_code == 'UNFINISHED_COMMIT':
                raise RequestError("`kaos train info` not available while job in state JOB_RUNNING")
            else:
                raise RequestError(r.text)

    def inspect(self):
        base_url = self.url
        name = self.workspace

        # get status of training queue
        r = requests.get(f"{base_url}/train/{name}/inspect", headers={"Token": self.token})
        if r.status_code == 200:
            data = r.json()
        else:
            data = {"image": "null", "data_glob": "null", "hyper_glob": "null"}
        return data

    def get_bundle(self, job_id, include_code, include_data, include_model, model_id):
        base_url = self.url
        name = self.workspace

        # GET /train/<name>/<job_id>/bundle
        r = requests.get(f"{base_url}/train/{name}/{job_id}/bundle",
                         params={
                             "include_code": include_code,
                             "include_data": include_data,
                             "include_model": include_model,
                             "model_id": model_id
                         })

        if r.status_code < 300:
            return name, r.content
        elif 400 <= r.status_code < 500:
            err = Error.from_dict(r.json())
            raise RequestError(err.message)
        else:
            raise RequestError(r.text)

    def provenance(self, out_dir, model_id):
        base_url = self.url
        name = self.workspace

        # build output directory (default = workspace)
        prov_dir = build_dir(out_dir, name, 'provenance')

        # GET /train/<name>/<model_id>/provenance
        r = requests.get(f"{base_url}/train/{name}/{model_id}/provenance", headers={"Token": self.token})

        if r.status_code < 300:
            out_fid = os.path.join(prov_dir, f"model-{model_id}")
            return out_fid, r.json()
        elif 400 <= r.status_code < 500:
            err = Error.from_dict(r.json())
            raise RequestError(err.message)
        else:
            raise RequestError(r.text)

    def get_train_logs(self, job_id):
        base_url = self.url
        name = self.workspace

        # GET /train/<name>/<job_id>/logs
        r = requests.get(f"{base_url}/train/{name}/{job_id}/logs", headers={"Token": self.token})

        if r.status_code < 300:
            return r.json()
        elif 400 <= r.status_code < 500:
            err = Error.from_dict(r.json())
            raise RequestError(err.message)
        else:
            raise RequestError(r.text)

    def kill_job(self, job_id):
        base_url = self.url
        workspace = self.workspace

        # GET /train/<workspace>/<job_id>
        r = requests.delete(f"{base_url}/train/{workspace}/{job_id}", headers={"Token": self.token})

        if r.status_code < 300:
            return r.json()
        elif 400 <= r.status_code < 500:
            err = Error.from_dict(r.json())
            raise RequestError(err.message)
        else:
            raise RequestError(r.text)

    def write_train_logs(self, job_id, logs, out_dir):
        name = self.workspace

        log_dir = build_dir(out_dir, name, 'logs')

        # save to file
        with open(os.path.join(log_dir, f"train-{job_id}.log"), 'w') as dst:
            dst.write(logs)

    def get_build_logs(self, job_id):
        base_url = self.url
        name = self.workspace

        # GET /train/<name>/<job_id>/logs
        r = requests.get(f"{base_url}/build/{name}/{job_id}/logs", headers={"Token": self.token})

        if r.status_code >= 300:
            err = Error.from_json(r.json())
            raise RequestError(err.message)

        return r.json()

    def write_build_logs(self, job_id, logs, out_dir):
        name = self.workspace

        log_dir = build_dir(out_dir, name, 'logs')

        # save to file
        with open(os.path.join(log_dir, f"build-train-{job_id}.log"), 'w') as dst:
            dst.write(logs)

    def upload_source_bundle(self, bundle_file, **kwargs):
        base_url = self.url
        user = self.user
        name = self.workspace

        kwargs['user'] = user
        with open(bundle_file, 'rb') as data:
            r = upload_with_progress_bar(data, f"{base_url}/train/{name}", kwargs, "  Uploading source bundle",
                                         self.token)

        if r.status_code < 300:
            return r.json()
        elif 400 <= r.status_code < 500:
            err = Error.from_dict(r.json())
            raise RequestError(err.message)
        else:
            raise RequestError(r.text)

    def upload_data_bundle(self, bundle_file, **kwargs):
        base_url = self.url
        name = self.workspace
        user = self.user
        kwargs['user'] = user
        with open(bundle_file, 'rb') as data:
            r = upload_with_progress_bar(data, f"{base_url}/data/{name}/features", kwargs, "  Uploading data bundle",
                                         self.token)

        if r.status_code < 300:
            return r.json()
        elif 400 <= r.status_code < 500:
            err = Error.from_dict(r.json())
            raise RequestError(err.message)
        else:
            raise RequestError(r.text)

    def upload_manifest(self, manifest_file, **kwargs):
        base_url = self.url
        name = self.workspace
        user = self.user

        kwargs['user'] = user

        with open(manifest_file, 'rb') as manif_f:
            r = upload_with_progress_bar(manif_f,
                                         f"{base_url}/data/{name}/manifest",
                                         kwargs,
                                         "  Uploading manifest bundle", self.token)

            if r.status_code < 300:
                return r.json()
            elif 400 <= r.status_code < 500:
                err = Error.from_dict(r.json())
                raise RequestError(err.message)
            else:
                raise RequestError(r.text)

    def upload_hyperparams(self, hyperparams_file=None, **kwargs):
        base_url = self.url
        name = self.workspace
        user = self.user

        kwargs['user'] = user

        if hyperparams_file:
            f = open(hyperparams_file, 'r').read()
            label = "  Uploading (hyper)parameters bundle"
        else:
            f = json.dumps({})
            label = None

        r = upload_with_progress_bar(f, f"{base_url}/data/{name}/params", kwargs, label=label, token=self.token)

        if r.status_code < 300:
            return r.json()
        elif 400 <= r.status_code < 500:
            err = Error.from_dict(r.json())
            raise RequestError(err.message)
        else:
            raise RequestError(r.text)

    @staticmethod
    def get_job_by_ind(ind):
        data = validate_cache(TRAIN_CACHE, command='train')
        loc = validate_index(len(data), ind, command='train')
        return data[loc]['job_id']

    @staticmethod
    def cache(data):
        # dump to "cache"
        with open(TRAIN_CACHE, 'w') as fp:
            json.dump(data, fp)
