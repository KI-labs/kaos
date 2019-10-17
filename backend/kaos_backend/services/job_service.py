import binascii
import datetime as dt
import glob
import json
import os
from typing import List
from io import StringIO

import docker
import python_pachyderm.client.pps.pps_pb2 as proto
from flask import current_app as app
from kaos_backend.clients.pachyderm import PachydermClient
from kaos_backend.constants import BUILD_IMAGE, BUILD_NOTEBOOK_PIPELINE_PREFIX, BUILD_SERVE_PIPELINE_PREFIX, \
    BUILD_TRAIN_PIPELINE_PREFIX, CLOUD_PROVIDER, TRAIN_DATA_REPO_PREFIX, \
    DOCKER_REGISTRY, EMPTY_HYPER_FILE, EMPTY_DATA_FILE, EMPTY_IMAGE_NAME, EMPTY_REGISTRY_NAME, HYPER_REPO_PREFIX, \
    JOB_STATE, LOCAL, MODEL_REPO_PREFIX, NOTEBOOK_IMAGE_REPO_PREFIX, \
    NOTEBOOK_PIPELINE_PREFIX, NOTEBOOK_SOURCE_REPO_PREFIX, \
    PIPELINE_STATE, PRED_ROUTE, SERVE_IMAGE_REPO_PREFIX, SERVE_PIPELINE_PREFIX, \
    SERVE_SOURCE_REPO_PREFIX, SERVICE_HOST, TRAIN_IMAGE_REPO_PREFIX, \
    TRAIN_PIPELINE_PREFIX, TRAIN_SOURCE_REPO_PREFIX, NOTEBOOK_DATA_REPO_PREFIX, TRAIN_DATA_MOUNT_PATH, \
    INGESTION_PIPELINE_PREFIX, MANIFEST_REPO_PREFIX
from kaos_backend.exceptions.exceptions import JobNotFoundError, NotebookAlreadyExistsError, PipelineNotFoundError, \
    ModelNotFoundError, UnfinishedCommitError, MetricNotFound, AlienProvenanceError
from kaos_backend.util.docker import get_login_command, create_docker_repo, delete_docker_repo
from kaos_backend.util.error_handling import recover
from kaos_backend.util.metadata import build_resource_meta, build_serve_regex
from kaos_backend.util.utility import repeated_call
from kaos_backend.util.validators import validate_resources
from kaos_model.common import WorkspaceInfo, DataDescriptor, PartitionInfo, \
    JobInfo, ServeInfo, ModelInfo, SubmissionInfo


class JobService:
    """
    Encapsulates all kaos-specific logic associated with Pachyderm. Includes the naming logic.

    We do ___NOT___ know about Pachyderm above

    We do ___NOT___ know about kaos workspaces below
    """

    SERVICE_TYPE = "ClusterIP"

    def __init__(self, client: PachydermClient):
        self.client = client
        self.docker_client = docker.from_env()

    @staticmethod
    def put_pipeline_arguments(source_dir, **kwargs):
        root_dir = os.listdir(source_dir)[0]
        pipeline_path = os.path.join(source_dir, root_dir, "pipeline_args.json")
        with open(pipeline_path, "w") as f:
            json.dump(kwargs, f)

    def get_service_pipeline_info(self,
                                  workspace: str,
                                  pipeline_name: str,
                                  provenance: bool = False):
        app.logger.debug("@%s: get service pipeline info %s", JobService.__name__, pipeline_name)

        info = self.client.inspect_pipeline(pipeline_name)

        if info.description:
            desc = json.loads(info.description)
        else:
            desc = {}

        image_descriptor = None
        code_descriptor = None
        model_info = None

        if provenance:
            app.logger.debug("@%s: get pipeline %s provenance", JobService.__name__, pipeline_name)

            # determine datum from endpoint name
            job_id = self.client.get_jobs(pipeline_name)[0].job.id
            datum = self.client.list_datum(job_id)[0]
            data = list(datum.datum_info.data)

            # get build image input
            data_input = next(filter(lambda d: d.file.commit.repo.name.startswith(BUILD_SERVE_PIPELINE_PREFIX), data))

            # convert the "image" datum to "code"
            image_repo = data_input.file.commit.repo.name
            image_path = data_input.file.path

            # TODO -> understand why service pipeline datum is "incorrect" -> commit not closed?
            objs = self.client.list_file(f"{image_repo}/master", path=image_path, history=-1)[0]
            image_commit = objs.file.commit.id

            # get source bundle input
            code_input = next(filter(lambda x: x.commit.repo.name != '__spec__',
                                     self.client.inspect_commit(f"{image_repo}/{image_commit}").provenance))
            code_repo = code_input.commit.repo.name
            code_commit = code_input.commit.id

            # determine path of source bundle (check with "actual" commit)
            objs = self.client.list_file(f"{code_repo}/{code_commit}", path='/', history=-1)
            obj = list(filter(lambda x: x.file.commit.id == code_commit, objs))[0]
            code_path = obj.file.path

            image_descriptor = DataDescriptor(
                repo=image_repo,
                commit=image_commit,
                path=image_path
            )

            code_descriptor = DataDescriptor(
                repo=code_repo,
                commit=code_commit,
                path=code_path
            )

            desc = json.loads(self.client.inspect_commit(f"{code_repo}/{code_commit}").description)
            if 'path' in desc:
                model_id = desc['path']
                model_info = self.get_model_info(workspace, model_id)
            else:
                app.logger.debug("@%s: %s deployed with alien model", JobService.__name__, pipeline_name)
                raise AlienProvenanceError

        return ServeInfo(
            name=pipeline_name,
            url=f"{SERVICE_HOST}/{pipeline_name}/{PRED_ROUTE}",
            user=desc.get('user'),
            state=PIPELINE_STATE[info.state],
            created_at=str(dt.datetime.fromtimestamp(info.created_at.seconds)),
            image=image_descriptor,
            code=code_descriptor,
            model=model_info
        )

    def get_notebook_info(self, pipeline_name: str):
        app.logger.debug("@%s: get notebook info %s", JobService.__name__, pipeline_name)

        info = self.client.inspect_pipeline(pipeline_name)

        if info.description:
            desc = json.loads(info.description)
        else:
            desc = {}

        return ServeInfo(
            name=pipeline_name,
            url=f"{SERVICE_HOST}/{pipeline_name}/lab",
            user=desc.get('user'),
            state=PIPELINE_STATE[info.state],
            created_at=str(dt.datetime.fromtimestamp(info.created_at.seconds))
        )

    def get_training_info(self, workspace: str, job_id: str, extract_metric=None):
        app.logger.debug("@%s: get training info %s in workspace %s", JobService.__name__, job_id, workspace)

        # check if train pipeline exists
        pipeline = f"{TRAIN_PIPELINE_PREFIX}-{workspace}"
        if not self.client.check_pipeline_exists(pipeline):
            raise PipelineNotFoundError(pipeline)

        # handle incomplete jobs
        if not self.client.check_job_exists(f"{TRAIN_PIPELINE_PREFIX}-{workspace}", job_id):
            raise JobNotFoundError(job_id)

        # get job info
        info = self.client.get_job_info(job_id)

        # determine output based on commit
        model_repo = info.output_commit.repo.name
        model_commit = info.output_commit.id

        # only use "processed" datums
        datums = self.client.list_datum(job_id)
        hyper_opt = True if len(datums) > 1 else False
        datums = list(filter(lambda x: x.datum_info.state == 1, datums))

        available_metrics = set()

        # format output

        partitions = []
        for datum in datums:

            # get all parts of the datum
            data = list(datum.datum_info.data)
            image_input = next(
                filter(lambda d: d.file.commit.repo.name.startswith(BUILD_TRAIN_PIPELINE_PREFIX), data))
            data_input = next(filter(lambda d: d.file.commit.repo.name.startswith(TRAIN_DATA_REPO_PREFIX), data))

            app.logger.info("@%s: image input %s", JobService.__name__, image_input)

            hyper_input = next(filter(lambda d: d.file.commit.repo.name.startswith(HYPER_REPO_PREFIX), data))

            # convert the "image" datum to "code"
            image_repo = image_input.file.commit.repo.name
            image_commit = image_input.file.commit.id
            image_path = image_input.file.path
            output_branch = self.build_output_branch(image_input.file.path, data_input.file.path, hyper_input.file.path)

            app.logger.info("@%s: inspecting commit %s/%s", JobService.__name__, image_repo, image_commit)

            code_repo = f"{TRAIN_SOURCE_REPO_PREFIX}-{workspace}"
            image_hash = output_branch.split('_')[0]
            obj = self.client.list_file(f"{code_repo}/master", path=f"/*{image_hash}", history=-1)[0]
            code_commit = obj.file.commit.id
            code_path = os.path.split(obj.file.path)[0]

            data_repo = f"{MANIFEST_REPO_PREFIX}-{workspace}"
            data_info = self.client.inspect_commit(f"{TRAIN_DATA_REPO_PREFIX}-{workspace}/{data_input.file.commit.id}")
            app.logger.debug(data_info.provenance)
            data_commit = \
                ["/".join([s.commit.repo.name, s.commit.id])
                 for s in data_info.provenance if s.commit.repo.name == data_repo][0]
            app.logger.debug(data_repo)
            app.logger.debug(data_commit)
            data_desc = json.loads(self.client.inspect_commit(data_commit).description)
            code_desc = json.loads(self.client.inspect_commit(
                f"{code_repo}/{code_commit}").description)
            hyper_desc = json.loads(self.client.inspect_commit(
                f"{HYPER_REPO_PREFIX}-{workspace}/{hyper_input.file.commit.id}").description)

            # separate logic for hyperopt since multiple files are on a single commit (only stats has "truth")
            if hyper_opt:
                objs = self.client.list_file(f"{model_repo}/stats", path=f"/{datum.datum_info.datum.id}/pfs/out")[0]
            else:
                objs = self.client.list_file(f"{model_repo}/{model_commit}", path="/")

            model_ids = [os.path.split(obj.file.path)[-1] for obj in objs]

            for model_id in model_ids:
                # extract metrics (if present)
                score = None
                glob_path = f"/{model_id}/metrics/**metrics**.json"
                if self.client.list_file(f"{model_repo}/{model_commit}", path=glob_path):
                    metrics_bytes = self.client.get_blob(repo=model_repo, commit=model_commit, path=glob_path)

                    metrics = json.loads(metrics_bytes)
                    available_metrics.update(list(metrics.keys()))
                    if extract_metric:
                        if extract_metric not in metrics:
                            raise MetricNotFound(extract_metric)
                        score = f"{metrics.get(extract_metric):0.4f}"

                code_descriptor = DataDescriptor(
                    repo=code_repo,
                    commit=code_commit,
                    path=code_path,
                    author=code_desc["user"]
                )

                data_descriptor = DataDescriptor(
                    repo=data_input.file.commit.repo.name,
                    commit=data_input.file.commit.id,
                    path=data_input.file.path,
                    author=data_desc["user"]
                )

                image_descriptor = DataDescriptor(
                    repo=image_repo,
                    commit=image_commit,
                    path=image_path
                )

                output_descriptor = DataDescriptor(
                    repo=model_repo,
                    commit=model_commit,
                    path=":".join([output_branch, model_id])
                )

                hyperparams = None
                # check if an "actual" hyperopt job (i.e. not empty)
                if self.check_hyperopt(hyper_input.file.path):
                    hyperparams = DataDescriptor(
                        repo=hyper_input.file.commit.repo.name,
                        commit=hyper_input.file.commit.id,
                        path=hyper_input.file.path,
                        author=hyper_desc["user"]
                    )

                partition_info = PartitionInfo(
                    code=code_descriptor,
                    data=data_descriptor,
                    image=image_descriptor,
                    datum_id=datum.datum_info.datum.id,
                    score=score,
                    hyperparams=hyperparams,
                    output=output_descriptor
                )

                partitions.append(partition_info)

        return JobInfo(
            job_id=info.job.id,
            state=JOB_STATE[info.state],
            process_time=info.stats.process_time.ToTimedelta().seconds,
            available_metrics=list(available_metrics),
            partitions=partitions
        )

    def get_model_provenance(self, workspace: str, commit_id: str, model_id: str) -> PartitionInfo:
        app.logger.debug("@%s: get model %s provenance in workspace %s", JobService.__name__, commit_id, workspace)

        jobs = self.client.get_jobs(f"{MODEL_REPO_PREFIX}-{workspace}")
        job_id = list(filter(lambda x: x.output_commit.id == commit_id, jobs))[0].job.id
        job_info = self.get_training_info(workspace, job_id)
        partition = next(filter(lambda p: os.path.split(p.output.path)[-1] == model_id, job_info.partitions))
        return partition

    def get_model_info(self, workspace: str, model_id: str):
        app.logger.debug("@%s: get model %s description in workspace %s", JobService.__name__, model_id, workspace)

        # define workspace-specific repo names
        model_repo = f"{MODEL_REPO_PREFIX}-{workspace}"
        train_source_repo = f"{TRAIN_SOURCE_REPO_PREFIX}-{workspace}"

        # retrieve obj corresponding to trained model object
        output_branch, model_prefix = model_id.split(':')
        if not self.client.check_branch_exists(model_repo, output_branch):
            raise ModelNotFoundError(model_id)
        head_commit = self.get_head_commit(model_prefix, output_branch, model_repo)
        obj = self.client.list_file(f"{model_repo}/{head_commit}", path=f"/{model_prefix}/model/",
                                    history=-1)
        if not obj:
            raise ModelNotFoundError(model_id)
        else:
            obj = obj[0]
        size = float(obj.size_bytes) / (1024 * 1024)  # convert to MB
        model_path = obj.file.path

        # get provenance of SOURCE-TRAIN
        info = self.client.inspect_commit(f"{model_repo}/{obj.file.commit.id}")
        prov_src = \
            ["/".join([s.commit.repo.name, s.commit.id])
             for s in info.provenance if s.commit.repo.name == train_source_repo][0]
        prov_src_info = self.client.inspect_commit(prov_src)
        if prov_src_info.description:
            desc = json.loads(prov_src_info.description)
        else:
            desc = {}

        return ModelInfo(
            user=desc.get('user'),
            commit_id=obj.file.commit.id,
            size=f"{size:.1f}MB",
            path=model_path,
            base_path=f"/{model_prefix}",
            model_id=model_id,
            created_at=str(dt.datetime.fromtimestamp(info.finished.seconds))
        )

    def recover_list_datum(self, job_id: str):
        app.logger.debug("@%s: recover list datum %s", JobService.__name__, job_id)

        return recover(lambda: self.client.list_datum(job_id), [UnfinishedCommitError], lambda: [])

    def list_training_jobs(self, workspace: str):
        app.logger.debug("@%s: list training jobs in workspace %s", JobService.__name__, workspace)
        return self.__list_jobs(f"{TRAIN_PIPELINE_PREFIX}-{workspace}", training=True)

    def list_build_serve_jobs(self, workspace: str):
        app.logger.debug("@%s: list build serve jobs in workspace %s", JobService.__name__, workspace)
        return self.__list_jobs(f"{BUILD_SERVE_PIPELINE_PREFIX}-{workspace}")

    def list_build_train_jobs(self, workspace: str):
        app.logger.debug("@%s: list build train jobs in workspace %s", JobService.__name__, workspace)
        return self.__list_jobs(f"{BUILD_TRAIN_PIPELINE_PREFIX}-{workspace}")

    def list_ingestion_jobs(self, workspace: str):
        app.logger.debug("@%s: list ingestion jobs in workspace %s", JobService.__name__, workspace)
        return self.__list_jobs(f"{INGESTION_PIPELINE_PREFIX}-{workspace}")

    def __list_jobs(self, pipeline_name: str, training=False) -> List[SubmissionInfo]:
        result = []
        if not self.client.check_pipeline_exists(pipeline_name):
            raise PipelineNotFoundError(pipeline_name)
        else:
            # get all jobs from client (by workspace)
            jobs = self.client.get_jobs(pipeline_name=pipeline_name)

            # filter jobs that were not COMPLETELY skipped
            jobs = list(filter(lambda x: x.data_skipped != x.data_total, jobs))

            # sort based on creation
            jobs.sort(key=lambda x: x.finished.seconds, reverse=True)

            # iterate through jobs
            for job in jobs:
                # FIXME -> error if datums do NOT have a valid output commit!!!
                # only use "processed" datums
                datums = self.recover_list_datum(job.job.id)
                datums = list(filter(lambda x: x.datum_info.state == 1, datums))
                n_datums = len(datums)
                total_seen = job.data_failed + job.data_processed + job.data_skipped
                duration = job.finished.seconds - job.started.seconds
                job_desc = SubmissionInfo(
                    job_id=job.job.id,
                    state=JOB_STATE[job.state],
                    started=str(dt.datetime.fromtimestamp(job.started.seconds)),
                    duration=duration if duration >= 0 else "?",
                    progress=f"Progress: {total_seen} / {job.data_total} ({(total_seen / job.data_total):.2%})"
                    f"\n{job.data_failed} failed\n{job.data_skipped} skipped"
                )

                if training:
                    job_desc.hyperopt = str(n_datums > 1) if duration >= 0 else "?"

                # save job overview
                result.append(job_desc)

            return result

    def list_notebooks(self, workspace: str):
        app.logger.debug("@%s: list notebooks in %s", JobService.__name__, workspace)

        pipelines = [p for p in self.client.list_pipelines() if p.startswith(f"{NOTEBOOK_PIPELINE_PREFIX}-{workspace}")]
        return [self.get_notebook_info(pipeline) for pipeline in pipelines]

    def list_building_notebooks(self, workspace: str):
        app.logger.debug("@%s: list building notebooks in workspace %s",
                         JobService.__name__, workspace)
        return self.__list_jobs(f"{BUILD_NOTEBOOK_PIPELINE_PREFIX}-{workspace}")

    @validate_resources
    def submit_notebook_code(self, workspace: str, user: str, source_dir: str, cpu=None, memory=None, gpu=0):
        app.logger.debug("@%s: submit notebook code in workspace %s for user %s", JobService.__name__, workspace,
                         user)
        pipeline_name = f"{NOTEBOOK_PIPELINE_PREFIX}-{workspace}-{user}"

        self.check_notebook_pipeline_exists(pipeline_name)

        # build description
        desc = build_resource_meta(workspace, user)
        self.put_pipeline_arguments(source_dir, cpu=cpu, memory=memory, gpu=gpu)
        return self.client.put_dir(f'{NOTEBOOK_SOURCE_REPO_PREFIX}-{workspace}', source_dir, desc=desc)

    def check_notebook_pipeline_exists(self, pipeline_name):
        if self.client.check_pipeline_exists(pipeline_name):
            app.logger.debug("@%s: notebook %s already exists", JobService.__name__, pipeline_name)
            raise NotebookAlreadyExistsError(pipeline_name)

    def define_notebook_pipeline(self,
                                 workspace: str,
                                 user: str,
                                 registry: str,
                                 image_name: str,
                                 cpu: float = None,
                                 memory: str = "512Mi",
                                 gpu: int = 0):
        app.logger.debug("@%s: create notebook in workspace %s for user %s", JobService.__name__, workspace, user)

        # deploy notebook
        pipeline_name = f"{NOTEBOOK_PIPELINE_PREFIX}-{workspace}-{user}"

        notebook_repo_name = f"{NOTEBOOK_DATA_REPO_PREFIX}-{workspace}"
        image_repo_name = f"{NOTEBOOK_IMAGE_REPO_PREFIX}-{workspace}"
        branch = "master"

        data_repo = proto.Input(pfs=proto.PFSInput(glob="/",
                                                   repo=notebook_repo_name,
                                                   branch='master',
                                                   name=notebook_repo_name))

        image_repo = proto.Input(pfs=proto.PFSInput(glob=f"/{image_name}",
                                                    repo=image_repo_name,
                                                    name=image_repo_name,
                                                    branch=branch))

        input_repo = proto.Input(cross=[data_repo, image_repo])

        # check if notebook exists
        self.check_notebook_pipeline_exists(pipeline_name)

        notebook_commands = [
            f"jupyter lab --ip 0.0.0.0 --port 8888 --no-browser --allow-root "
            f"--NotebookApp.token='{user}' --NotebookApp.base_url='{pipeline_name}'"
        ]

        image_name = f"{registry}/{image_name}" if CLOUD_PROVIDER != LOCAL else image_name
        env = {"DATA_REPO": f"{notebook_repo_name}"}

        self.define_service_pipeline(pipeline_name=pipeline_name,
                                     image_name=image_name,
                                     commands=notebook_commands,
                                     internal_port=8888,
                                     external_port=30914,
                                     input_repo=input_repo,
                                     desc=build_resource_meta(workspace, user),
                                     preserve_path=True,
                                     use_websocket=True,
                                     env=env,
                                     cpu=cpu,
                                     memory=memory,
                                     gpu=gpu)
        return pipeline_name

    @validate_resources
    def build_inference_with_model_id(self,
                                      workspace: str,
                                      user: str,
                                      model_id: str,
                                      source_dir: str,
                                      cpu: float = None,
                                      memory: str = None,
                                      gpu: int = 0):
        app.logger.debug("@%s: build inference with model %s in workspace %s for user %s", JobService.__name__,
                         model_id, workspace, user)

        glob_p = os.path.split(next(glob.iglob(f"{source_dir}/**/serve", recursive=True)))[0]
        temp_path = os.path.join(source_dir, glob_p)

        desc = None
        if model_id:
            model_info = self.get_model_info(workspace, model_id)
            model_commit_id = model_info.commit_id
            model_path = os.path.join(f"/{model_info.base_path}", 'model')

            self.client.get_dir(f"{MODEL_REPO_PREFIX}-{workspace}",
                                model_commit_id,
                                model_path,
                                out_dir=temp_path,
                                remove_prefix=True)
            desc = build_resource_meta(user, workspace, commit_id=model_commit_id, path=model_id)

        self.put_pipeline_arguments(source_dir, cpu=cpu, memory=memory, gpu=gpu)
        self.inject_model(workspace, source_dir, desc)

    def inject_model(self, workspace: str, source_dir: str, desc: str):
        app.logger.debug("@%s: inject model in workspace %s", JobService.__name__, workspace)

        self.client.put_dir(f'{SERVE_SOURCE_REPO_PREFIX}-{workspace}', source_dir, desc=desc)

    def deploy_inference(self,
                         workspace: str,
                         user: str,
                         registry: str,
                         image_name: str,
                         ambassador_timeout: int = 30000,
                         cpu: float = None,
                         memory: str = "512Mi",
                         gpu: int = 0):
        app.logger.debug("@%s: deploy inference in workspace %s - %s with image name %s",
                         JobService.__name__, workspace, user, image_name)

        rand = binascii.b2a_hex(os.urandom(3)).decode('utf-8')
        pipeline_name = f"{SERVE_PIPELINE_PREFIX}-{workspace}-{rand}"

        image_repo_name = f"{SERVE_IMAGE_REPO_PREFIX}-{workspace}"
        branch = "master"

        image_repo = proto.Input(pfs=proto.PFSInput(glob=f"/{image_name}",
                                                    repo=image_repo_name,
                                                    name=image_repo_name,
                                                    branch=branch))

        image_name = f"{registry}/{image_name}" if CLOUD_PROVIDER != LOCAL else image_name
        self.define_service_pipeline(pipeline_name=pipeline_name,
                                     image_name=image_name,
                                     commands=["./serve"],
                                     external_port=30912,
                                     input_repo=image_repo,
                                     desc=build_resource_meta(workspace, user),
                                     preserve_path=False,
                                     ambassador_timeout=ambassador_timeout,
                                     cpu=cpu,
                                     memory=memory,
                                     gpu=gpu)

    @validate_resources
    def submit_training_code(self, workspace: str, user: str, source_dir: str, cpu=None, memory=None, gpu=0):
        app.logger.debug("@%s: submit training code in workspace %s for user %s", JobService.__name__, workspace,
                         user)

        desc = build_resource_meta(workspace, user)
        repo = f"{TRAIN_SOURCE_REPO_PREFIX}-{workspace}"
        if not self.check_duplicate_bundle(repo=repo, path=os.listdir(source_dir)[0]):
            self.put_pipeline_arguments(source_dir, cpu=cpu, memory=memory, gpu=gpu)
            self.client.put_dir(repo, source_dir, desc=desc)

    def submit_training_data(self, workspace: str, user: str, source_dir: str):
        app.logger.debug("@%s: submit training data in workspace %s for user %s",
                         JobService.__name__, workspace, user)

        desc = build_resource_meta(workspace, user)
        repo = f"{MANIFEST_REPO_PREFIX}-{workspace}"
        if not self.check_duplicate_bundle(repo=repo, path=os.listdir(source_dir)[0]):
            self.client.put_dir(repo, source_dir, desc=desc)

    def submit_notebook_data(self, workspace: str, user: str, source_dir: str):
        app.logger.debug("@%s: submit notebook in workspace %s for user %s", JobService.__name__, workspace, user)

        desc = build_resource_meta(workspace, user)
        self.client.put_dir(f'{NOTEBOOK_DATA_REPO_PREFIX}-{workspace}', source_dir, desc=desc)

    def submit_manifest(self, workspace: str, user: str, manifest_bytes, path: str):
        app.logger.debug("@%s: submit manifest file in workspace %s for user %s", JobService.__name__, workspace, user)

        repo = f"{MANIFEST_REPO_PREFIX}-{workspace}"
        desc = build_resource_meta(workspace, user)

        self.client.put_blob(repo, path, manifest_bytes, split_by_lines=True, desc=desc)

    def submit_params(self, workspace: str, user: str, params_lists: list, path: str):
        app.logger.debug("@%s: submit params in workspace %s for user %s", JobService.__name__, workspace, user)

        # avoid duplicate ingestion
        repo = f"{HYPER_REPO_PREFIX}-{workspace}"
        if not self.check_duplicate_bundle(repo=repo, path=path):

            desc = build_resource_meta(workspace, user)
            blobs = []
            for params in params_lists:
                # ensure same hyperparams are not run more than once.
                param_names = []
                for k, v in params.items():
                    param_names.append(f"{k}={v}")

                # fix naming of "empty" file
                name = os.path.join(path, "_".join(param_names) + ".json") if params else EMPTY_HYPER_FILE

                # commit params
                param_bytes = bytes(json.dumps(params), encoding='utf-8')
                blobs.append({'path': name, 'blob': param_bytes})

            self.client.put_blobs(repo, blobs, desc=desc)

    def list_endpoints(self, workspace: str):
        app.logger.debug("@%s: list endpoint in workspace %s", JobService.__name__, workspace)

        names = self.client.list_pipelines()
        pipelines = filter(build_serve_regex(workspace).match, names)
        return [self.get_service_pipeline_info(workspace, pipeline) for pipeline in pipelines]

    def list_building_endpoints(self, workspace: str):
        app.logger.debug("@%s: list building endpoints in workspace %s",
                         JobService.__name__, workspace)
        return self.__list_jobs(f"{BUILD_SERVE_PIPELINE_PREFIX}-{workspace}")

    def check_duplicate_bundle(self, repo: str, path: str):
        app.logger.debug("@%s: checking duplicate bundle [%s] in %s", JobService.__name__, path, repo)
        try:
            if self.list_objects(repo=repo, path=path):
                app.logger.debug("@%s: duplicate bundle found [%s]", JobService.__name__, path)
                return True
        except json.decoder.JSONDecodeError:
            pass

    def list_objects(self, repo: str, commit: str = "master", path: str = "/"):
        app.logger.debug("@%s: list objects in repository %s by commit %s", JobService.__name__, repo, commit)
        obj_list = self.client.list_file(f"{repo}/{commit}", path=path, history=-1)
        return list(filter(lambda x: self.client.inspect_file(f"{repo}/{commit}", x.file.path).size_bytes != 0,
                           obj_list))

    def delete_endpoint(self, endpoint_name):
        app.logger.debug("@%s: delete endpoint %s", JobService.__name__, endpoint_name)

        # check if notebook exists
        exists = self.client.check_pipeline_exists(endpoint_name)
        if not exists:
            raise PipelineNotFoundError(endpoint_name)

        return self.client.delete_pipeline(endpoint_name)

    def delete_train_job(self, workspace, job_id):
        app.logger.debug("@%s: delete train job %s in workspace %s", JobService.__name__, job_id, workspace)

        train_pipeline = f"{TRAIN_PIPELINE_PREFIX}-{workspace}"

        return self.client.delete_job(train_pipeline, job_id)

    def delete_build_train_job(self, workspace, job_id):
        app.logger.debug("@%s: delete build train job %s in workspace %s", JobService.__name__, job_id, workspace)

        build_train_pipeline = f"{BUILD_TRAIN_PIPELINE_PREFIX}-{workspace}"

        return self.client.delete_job(build_train_pipeline, job_id)

    def define_bundle_ingestion_pipeline(self, workspace: str, user: str, data_glob: str):
        app.logger.debug("@%s: build ingestion pipeline in workspace %s for user %s", JobService.__name__,
                         workspace, user)

        pipeline_name = f"{INGESTION_PIPELINE_PREFIX}-{workspace}"
        manifest_repo = f"{MANIFEST_REPO_PREFIX}-{workspace}"

        commands = [
            "set -v",
            f"cp -r /pfs/{manifest_repo}/{data_glob}/ /pfs/out",
        ]

        pfs_input = proto.Input(pfs=proto.PFSInput(
            glob=f"/{data_glob}/*",
            repo=manifest_repo,
            branch='master',
            name=manifest_repo)
        )

        return self.client.create_pipeline(name=pipeline_name,
                                           image="dwdraju/alpine-curl-jq",
                                           commands=commands,
                                           update=True,
                                           description="Ingestion pipeline",
                                           pfs_input=pfs_input)

    def define_manifest_ingestion_pipeline(self, workspace: str, user: str, data_glob: str):
        app.logger.debug("@%s: build ingestion pipeline in workspace %s for user %s", JobService.__name__,
                         workspace, user)

        pipeline_name = f"{INGESTION_PIPELINE_PREFIX}-{workspace}"
        manifest_repo = f"{MANIFEST_REPO_PREFIX}-{workspace}"

        commands = [
            "set -v",
            f"for name in /pfs/{manifest_repo}/{data_glob}/*",
            "do",
            "echo $name",
            "export URL=`cat $name | jq -r '.url'`",
            "export PTH=`cat $name | jq -r '.path'`",
            "echo $URL",
            "echo $PTH",
            f'curl --create-dirs -o /pfs/out/{data_glob}/$PTH $URL',
            "done",
        ]

        pfs_input = proto.Input(pfs=proto.PFSInput(
            glob=f"/{data_glob}/*",
            repo=manifest_repo,
            branch='master',
            name=manifest_repo)
        )

        return self.client.create_pipeline(name=pipeline_name,
                                           image="dwdraju/alpine-curl-jq",
                                           commands=commands,
                                           update=True,
                                           description="Ingestion pipeline",
                                           parallelism=3,
                                           pfs_input=pfs_input,
                                           cpu=0.2,
                                           memory="512Mi",
                                           standby=True)

    def __define_build_pipeline(self,
                                pipeline_name: str,
                                description: str,
                                source_repo: str,
                                env=None,
                                callback=None):
        app.logger.debug("@%s: build pipeline %s", JobService.__name__, pipeline_name)

        image_name = f"{DOCKER_REGISTRY}/{pipeline_name}" if CLOUD_PROVIDER != LOCAL else pipeline_name
        create_docker_repo(pipeline_name)
        login_command = get_login_command()

        commands = [
            f"pather=/pfs/{source_repo}",
            "for name in $pather/*",
            "do",
            "name=$(basename $name)",
            login_command,
            "image_tag=${name##*:}",
            f"docker build --no-cache -t {image_name}:$image_tag --network=host "
            f"-f $pather/$name/Dockerfile $pather/$name/model > "
            f"/pfs/out/{pipeline_name}:$image_tag",
            f"docker push {image_name}:$image_tag" if CLOUD_PROVIDER != LOCAL else "",
            f'curl --retry 3 -vf -H "Content-Type: application/json" '
            f'-X POST "http://$BACKEND_SERVICE_HOST:$BACKEND_SERVICE_PORT{callback}'
            f'/$KAOS_WORKSPACE/$KAOS_USER?registry={DOCKER_REGISTRY}&image_name={pipeline_name}:$image_tag" '
            f'-d @$pather/$name/pipeline_args.json',
            "done"
        ]
        pfs_input = proto.Input(pfs=proto.PFSInput(glob="/*", repo=source_repo, branch='master', name=source_repo))

        return self.client.create_pipeline(name=pipeline_name,
                                           image=BUILD_IMAGE,
                                           commands=commands,
                                           description=description,
                                           pfs_input=pfs_input,
                                           env=env)

    def define_build_train_pipeline(self, workspace: str, user: str):
        app.logger.debug("@%s: build train pipeline in workspace %s for user %s", JobService.__name__, workspace, user)

        desc = build_resource_meta(workspace, user)
        env = {"KAOS_WORKSPACE": workspace, "KAOS_USER": user}
        pipeline_name = f"{BUILD_TRAIN_PIPELINE_PREFIX}-{workspace}"
        source_repo = f"{TRAIN_SOURCE_REPO_PREFIX}-{workspace}"

        return self.__define_build_pipeline(
            pipeline_name=pipeline_name,
            description=desc,
            source_repo=source_repo,
            env=env,
            callback="/internal/train_pipeline"
        )

    def define_build_notebook_pipeline(self, workspace: str, user: str):
        app.logger.debug("@%s: build notebook pipeline in workspace %s for user %s", JobService.__name__,
                         workspace, user)

        desc = build_resource_meta(workspace, user)
        env = {"KAOS_WORKSPACE": workspace, "KAOS_USER": user}
        pipeline_name = f"{BUILD_NOTEBOOK_PIPELINE_PREFIX}-{workspace}"
        source_repo = f"{NOTEBOOK_SOURCE_REPO_PREFIX}-{workspace}"

        return self.__define_build_pipeline(
            pipeline_name=pipeline_name,
            description=desc,
            source_repo=source_repo,
            env=env,
            callback="/internal/notebook_pipeline"
        )

    def define_build_serve_pipeline(self, workspace: str, user: str):
        app.logger.debug("@%s: build serve pipeline in workspace %s for user %s", JobService.__name__, workspace, user)

        desc = build_resource_meta(workspace, user)
        env = {"KAOS_WORKSPACE": workspace, "KAOS_USER": user}
        pipeline_name = f"{BUILD_SERVE_PIPELINE_PREFIX}-{workspace}"
        source_repo = f"{SERVE_SOURCE_REPO_PREFIX}-{workspace}"

        return self.__define_build_pipeline(
            pipeline_name=pipeline_name,
            description=desc,
            source_repo=source_repo,
            env=env,
            callback="/internal/serve_pipeline"
        )

    def build_output_branch(self, image_name: str, data_name: str, hyper_name: str):

        image_hex = image_name.split(':')[-1]
        data_hex = data_name.split(':')[-1].replace('/', '')
        temp = f"{image_hex}_{data_hex}"
        if self.check_hyperopt(hyper_name):
            hyper_hex = os.path.basename(os.path.split(hyper_name)[0])
            temp += f"_{hyper_hex}"
        return temp if temp.find('null') < 0 else 'null'

    @validate_resources
    def define_train_pipeline(self,
                              workspace: str,
                              user: str,
                              registry: str = EMPTY_REGISTRY_NAME,
                              image_name: str = EMPTY_IMAGE_NAME,
                              data_name: str = EMPTY_DATA_FILE,
                              hyper_name: str = EMPTY_HYPER_FILE,
                              parallelism: int = 1,
                              cpu: float = None,
                              memory: str = "512Mi",
                              gpu: int = 0):
        app.logger.debug("@%s: define train pipeline in workspace %s for user %s", JobService.__name__, workspace,
                         user)

        # "fixed" based on <workspace>
        pipeline_name = f"{TRAIN_PIPELINE_PREFIX}-{workspace}"

        if self.client.check_pipeline_exists(pipeline_name):
            payload = dict()
            if image_name != EMPTY_IMAGE_NAME:
                payload["image_glob"] = f"/{image_name}"
                payload["image"] = f"{registry}/{image_name}" if CLOUD_PROVIDER != LOCAL else image_name
            if data_name != EMPTY_DATA_FILE:
                payload["data_glob"] = f"/{data_name}"

            # add parallelism + hyper to payload (overwrites hyperopt if new code/data supplied)
            payload["parallelism"] = parallelism
            payload["cpu"] = cpu
            payload["memory"] = memory
            payload["gpu"] = gpu
            payload["hyper_glob"] = f"/{hyper_name}"
            return self.update_training_pipeline(pipeline_name, payload)

        # "fixed" based on <workspace>
        data_repo = f"{INGESTION_PIPELINE_PREFIX}-{workspace}"
        image_repo = f"{TRAIN_IMAGE_REPO_PREFIX}-{workspace}"
        hyper_repo = f"{HYPER_REPO_PREFIX}-{workspace}"
        desc = build_resource_meta(workspace, user)

        # build dynamic output_branch
        output_branch = self.build_output_branch(image_name, data_name, hyper_name)
        self.client.pfs_client.create_branch(repo_name=pipeline_name, branch_name=output_branch)

        data_input = proto.Input(pfs=proto.PFSInput(glob=f"/{data_name}",
                                                    repo=data_repo,
                                                    branch='master',
                                                    name=TRAIN_DATA_MOUNT_PATH))
        image_input = proto.Input(pfs=proto.PFSInput(glob=f"/{image_name}",
                                                     repo=image_repo,
                                                     branch='master',
                                                     name=TRAIN_IMAGE_REPO_PREFIX))
        hyper_input = proto.Input(pfs=proto.PFSInput(glob=f"/{hyper_name}",
                                                     repo=hyper_repo,
                                                     branch='master',
                                                     name=HYPER_REPO_PREFIX))

        pfs_input = proto.Input(cross=[data_input, image_input, hyper_input])

        train_command = [
            "rand=$(openssl rand -hex 3)",
            "./train /pfs/out/$rand"
        ]

        return self.client.create_pipeline(name=pipeline_name,
                                           image=f"{registry}/{image_name}" if CLOUD_PROVIDER != LOCAL else image_name,
                                           commands=train_command,
                                           description=desc,
                                           pfs_input=pfs_input,
                                           parallelism=parallelism,
                                           output_branch=output_branch,
                                           update=True,
                                           reprocess=False,
                                           cpu=cpu,
                                           memory=memory,
                                           gpu=gpu)

    @repeated_call(2)
    def update_training_pipeline(self, pipeline_name: str, payload: dict):
        app.logger.debug("@%s: update train pipeline %s", JobService.__name__, pipeline_name)

        pipeline_def = self.inspect_training_pipeline(pipeline_name)

        # only update if pipeline spec has changed!
        identical = all([payload[k] == pipeline_def[k] for k in list(payload.keys())])
        if not identical:

            pipeline_def.update(payload)

            # build dynamic output_branch
            pipeline_def["output_branch"] = self.build_output_branch(pipeline_def["image_glob"],
                                                                     pipeline_def["data_glob"],
                                                                     pipeline_def["hyper_glob"])

            app.logger.debug("output_branch")
            app.logger.debug(pipeline_def["output_branch"])

            if not self.client.check_branch_exists(repo=pipeline_name, branch=pipeline_def["output_branch"]):
                self.client.pfs_client.create_branch(repo_name=pipeline_name, branch_name=pipeline_def["output_branch"])

            # format according to create_pipeline
            data_input = proto.Input(pfs=proto.PFSInput(glob=pipeline_def["data_glob"],
                                                        repo=pipeline_def["data_repo"],
                                                        branch=pipeline_def["data_branch"],
                                                        name=pipeline_def["data_name"]))
            image_input = proto.Input(pfs=proto.PFSInput(glob=pipeline_def["image_glob"],
                                                         repo=pipeline_def["image_repo"],
                                                         branch=pipeline_def["image_branch"],
                                                         name=pipeline_def["image_name"]))
            hyper_input = proto.Input(pfs=proto.PFSInput(glob=pipeline_def["hyper_glob"],
                                                         repo=pipeline_def["hyper_repo"],
                                                         branch=pipeline_def["hyper_branch"],
                                                         name=pipeline_def["hyper_name"]))

            pfs_input = proto.Input(cross=[data_input, image_input, hyper_input])

            return self.client.create_pipeline(name=pipeline_name,
                                               image=pipeline_def["image"],
                                               commands=pipeline_def["commands"],
                                               description=pipeline_def["description"],
                                               pfs_input=pfs_input,
                                               parallelism=pipeline_def["parallelism"],
                                               gpu=pipeline_def["gpu"],
                                               memory=pipeline_def["memory"],
                                               cpu=pipeline_def["cpu"],
                                               output_branch=pipeline_def["output_branch"],
                                               update=True,
                                               reprocess=False)

    def inspect_training_pipeline(self, pipeline_name):
        app.logger.debug("@%s: inspect train pipeline %s", JobService.__name__, pipeline_name)

        # ensure pipeline exists
        if not self.client.check_pipeline_exists(pipeline_name):
            raise PipelineNotFoundError(pipeline_name)

        # get info -> format!
        pipeline_info = self.client.inspect_pipeline(pipeline_name)
        commands = list(pipeline_info.transform.stdin)
        commands.remove('set -e')

        # format to dict -> then update with payload
        pipeline_def = {
            "image": pipeline_info.transform.image,
            "commands": commands,
            "description": pipeline_info.description,
            "parallelism": pipeline_info.parallelism_spec.constant,
            "output_branch": pipeline_info.output_branch,
            "cpu": pipeline_info.resource_requests.cpu,
            "memory": pipeline_info.resource_requests.memory,
            "gpu": pipeline_info.resource_limits.gpu.number
        }

        # extract inputs
        input_names = ["data", "image", "hyper"]
        build_input = next(
            filter(lambda x: x.pfs.repo.startswith(BUILD_TRAIN_PIPELINE_PREFIX), pipeline_info.input.cross))
        data_input = next(filter(lambda x: x.pfs.repo.startswith(TRAIN_DATA_REPO_PREFIX), pipeline_info.input.cross))
        hyper_input = next(filter(lambda x: x.pfs.repo.startswith(HYPER_REPO_PREFIX), pipeline_info.input.cross))
        for n, p in zip(input_names, [data_input, build_input, hyper_input]):
            pipeline_def[f"{n}_name"] = p.pfs.name
            pipeline_def[f"{n}_repo"] = p.pfs.repo
            pipeline_def[f"{n}_branch"] = p.pfs.branch
            pipeline_def[f"{n}_glob"] = p.pfs.glob

        return pipeline_def

    def define_service_pipeline(self,
                                pipeline_name,
                                image_name,
                                commands=None,
                                internal_port=8080,
                                external_port=30912,
                                input_repo=None,
                                desc=None,
                                preserve_path=True,
                                ambassador_timeout=15000,
                                use_websocket=False,
                                env=None,
                                cpu: float = None,
                                memory: str = None,
                                gpu: int = 0):
        app.logger.debug("@%s: define service pipeline in %s", JobService.__name__, pipeline_name)

        commands = commands or ["serve"]

        ambassador_conf = f"""---
apiVersion: ambassador/v1
kind:  Mapping
name:  {pipeline_name}_mapping
prefix: /{pipeline_name}/
use_websocket: {"true" if use_websocket else "false"}
service: pipeline-{pipeline_name}-v1-user:{external_port}
connect_timeout_ms: {ambassador_timeout}
timeout_ms: {ambassador_timeout}
"""

        if preserve_path:
            ambassador_conf += "\nrewrite: \"\""

        annotations = {"getambassador.io/config": ambassador_conf}

        service = proto.Service(internal_port=internal_port,
                                external_port=external_port,
                                type=self.SERVICE_TYPE,
                                annotations=annotations)

        return self.client.create_pipeline(name=pipeline_name,
                                           image=image_name,
                                           commands=commands,
                                           description=desc,
                                           pfs_input=input_repo,
                                           standby=True,
                                           service=service,
                                           env=env,
                                           update=False,
                                           reprocess=False,
                                           cpu=cpu,
                                           memory=memory,
                                           gpu=gpu)

    @staticmethod
    def __build_repo_names(workspace: str):
        return [
            f"{TRAIN_DATA_REPO_PREFIX}-{workspace}",
            f"{TRAIN_IMAGE_REPO_PREFIX}-{workspace}",
            f"{TRAIN_SOURCE_REPO_PREFIX}-{workspace}",
            f"{MODEL_REPO_PREFIX}-{workspace}",
            f"{SERVE_SOURCE_REPO_PREFIX}-{workspace}",
            f"{NOTEBOOK_DATA_REPO_PREFIX}-{workspace}",
            f"{NOTEBOOK_IMAGE_REPO_PREFIX}-{workspace}",
            f"{NOTEBOOK_SOURCE_REPO_PREFIX}-{workspace}",
            f"{HYPER_REPO_PREFIX}-{workspace}",
            f"{MANIFEST_REPO_PREFIX}-{workspace}",
        ]

    @staticmethod
    def __build_pipeline_names(workspace: str):
        return [
            f"{BUILD_TRAIN_PIPELINE_PREFIX}-{workspace}",
            f"{TRAIN_PIPELINE_PREFIX}-{workspace}",
            f"{BUILD_SERVE_PIPELINE_PREFIX}-{workspace}",
            f"{BUILD_NOTEBOOK_PIPELINE_PREFIX}-{workspace}",
            f"{INGESTION_PIPELINE_PREFIX}-{workspace}"
        ]

    def init_workspace_repos(self, workspace: str, user: str):
        app.logger.debug("@%s: init workspace repos in %s", JobService.__name__, workspace)

        repo_names = JobService.__build_repo_names(workspace)

        repos = zip(repo_names,
                    [build_resource_meta(workspace, user)] * len(repo_names))

        for (repo, desc) in repos:
            self.client.create_repo(repo, desc=desc)

    def init_notebook_data(self, workspace: str, user: str):
        app.logger.debug("@%s: adding DUMMY notebook-data on %s", JobService.__name__, workspace)

        blob = [{'path': '.kaos',
                 'blob': bytes('dummy', encoding='utf-8')}]

        self.client.put_blobs(f"{NOTEBOOK_DATA_REPO_PREFIX}-{workspace}", blob, desc=user)

    def list_workspaces(self):
        app.logger.debug("@%s: list workspaces", JobService.__name__)

        all_pipelines = self.client.list_pipelines()
        all_repos = self.client.list_repos()
        services = tuple([SERVE_PIPELINE_PREFIX, NOTEBOOK_PIPELINE_PREFIX])
        names = list(set([x.split('-')[-1] for x in all_repos + all_pipelines if not x.startswith(services)]))
        return {'names': names}

    def check_workspace_available(self, workspace: str):
        app.logger.debug("@%s: check workspace %s available", JobService.__name__, workspace)

        repos = JobService.__build_repo_names(workspace)
        pipelines = JobService.__build_pipeline_names(workspace)

        no_repos = not any(map(lambda repo: self.client.check_repo_exists(repo), repos))
        no_pipelines = not any(map(lambda p: self.client.check_pipeline_exists(p), pipelines))

        return no_pipelines and no_repos

    def check_workspace_healthy(self, workspace: str):
        app.logger.debug("@%s: check workspace %s is healthy", JobService.__name__, workspace)

        repos = JobService.__build_repo_names(workspace)
        pipelines = JobService.__build_pipeline_names(workspace)

        all_repos = all(map(lambda repo: self.client.check_repo_exists(repo), repos))
        all_pipelines = all(map(lambda p: self.client.check_pipeline_exists(p), pipelines))

        return all_repos and all_pipelines

    def get_workspace(self, workspace: str):
        app.logger.debug("@%s: get workspace %s", JobService.__name__, workspace)

        # list all repos based on <workspace>
        all_repos = self.client.list_repos()
        repos = [repo for repo in all_repos if workspace in repo]

        # list all pipelines based on <workspace>
        all_pipelines = self.client.list_pipelines()
        pipelines = [pipeline for pipeline in all_pipelines if workspace in pipeline]

        return WorkspaceInfo(
            name=workspace,
            pipelines=pipelines,
            repos=repos
        )

    def kill_workspace(self, workspace):
        app.logger.debug("@%s: kill workspace %s", JobService.__name__, workspace)

        delete_docker_repo(f"{NOTEBOOK_IMAGE_REPO_PREFIX}-{workspace}")
        delete_docker_repo(f"{TRAIN_IMAGE_REPO_PREFIX}-{workspace}")
        delete_docker_repo(f"{SERVE_IMAGE_REPO_PREFIX}-{workspace}")

        workspace_info = self.get_workspace(workspace)
        for repo in workspace_info.repos:
            self.client.delete_repo(repo)
        for pipeline in workspace_info.pipelines:
            self.client.delete_pipeline(pipeline_name=pipeline)

    def __get_logs(self, pipeline_name: str, job_id=None):
        app.logger.debug("@%s: get logs by pipeline %s or job %s", JobService.__name__, pipeline_name, job_id)

        if job_id:
            logs = self.client.get_job_logs(pipeline_name=pipeline_name, job_id=job_id)
        else:
            logs = self.client.get_pipeline_logs(pipeline_name=pipeline_name)

        out = StringIO()

        # body
        for log in logs:
            ts = dt.datetime.fromtimestamp(log.ts.seconds)
            out.write(f"[{ts}] {log.message}\n")

        content = out.getvalue()
        out.close()

        return content

    def get_build_train_logs(self, workspace: str, job_id: str):
        app.logger.debug("@%s: get build train logs by job %s in workspace %s", JobService.__name__, job_id, workspace)
        return self.__get_logs(f"{BUILD_TRAIN_PIPELINE_PREFIX}-{workspace}", job_id)

    def get_build_notebook_logs(self, workspace: str, job_id: str):
        app.logger.debug("@%s: get build notebook logs by job %s in workspace %s", JobService.__name__, job_id,
                         workspace)
        return self.__get_logs(f"{BUILD_NOTEBOOK_PIPELINE_PREFIX}-{workspace}", job_id)

    def get_build_serve_logs(self, workspace: str, job_id: str):
        app.logger.debug("@%s: get build serve logs by job %s in workspace %s", JobService.__name__, job_id, workspace)
        return self.__get_logs(f"{BUILD_SERVE_PIPELINE_PREFIX}-{workspace}", job_id)

    def get_train_logs(self, workspace: str, job_id: str):
        app.logger.debug("@%s: get train logs by job %s in workspace %s", JobService.__name__, job_id, workspace)
        return self.__get_logs(f"{TRAIN_PIPELINE_PREFIX}-{workspace}", job_id)

    def get_serve_logs(self, endpoint_name):
        app.logger.debug("@%s: get inference logs by endpoint %s", JobService.__name__, endpoint_name)
        return self.__get_logs(endpoint_name)

    @staticmethod
    def check_hyperopt(name):
        return name != f"/{EMPTY_HYPER_FILE}"

    def download_serve_code(self, workspace: str, pipeline_name: str, out_dir: str):
        app.logger.debug("@%s: download serve code from pipeline %s in workspace %s", JobService.__name__,
                         pipeline_name, workspace)

        provenance = self.get_service_pipeline_info(workspace, pipeline_name, provenance=True)

        repo = f"{SERVE_SOURCE_REPO_PREFIX}-{workspace}"
        commit = provenance.code.commit
        path = provenance.code.path

        # get bundle
        self.client.get_dir(repo, commit, path, os.path.join(out_dir, 'code'))

    def download_train_output(self, workspace: str, model_commit_id: str, model_path: str, out_dir: str):
        app.logger.debug("@%s: download train output path %s from model commit %s in workspace %s",
                         JobService.__name__,
                         model_path, model_commit_id, workspace)

        self.client.get_dir(f"{MODEL_REPO_PREFIX}-{workspace}",
                            model_commit_id,
                            model_path,
                            out_dir=out_dir,
                            remove_prefix=False)

    def get_head_commit(self, path, branch, repo):
        commits = list(self.client.list_commit(repo,
                                               to_commit=f"{repo}/{branch}"))
        return list(filter(lambda x: x.size_bytes != 0, commits))[0].commit.id

    def download_by_info(self, data_descriptor: DataDescriptor, out_dir: str):
        app.logger.debug("@%s: download by info %s", JobService.__name__, data_descriptor)
        self.client.get_dir(data_descriptor.repo,
                            data_descriptor.commit,
                            data_descriptor.path,
                            out_dir=out_dir,
                            remove_prefix=False)

    def destroy_pachyderm_resources(self):
        app.logger.debug("@%s: destroy pachyderm resources", JobService.__name__)
        self.client.delete_all()

    def get_datum_by_job_id(self, workspace, job_id):
        return self.get_training_info(workspace, job_id).partitions

    def check_train_job_exists(self, workspace, job_id):
        train_pipeline = f"{TRAIN_PIPELINE_PREFIX}-{workspace}"
        return self.client.check_job_exists(train_pipeline, job_id)

    def check_build_train_job_exists(self, workspace, job_id):
        build_train_pipeline = f"{BUILD_TRAIN_PIPELINE_PREFIX}-{workspace}"
        return self.client.check_job_exists(build_train_pipeline, job_id)

    def check_train_job_running(self, workspace, job_id):
        train_pipeline = f"{TRAIN_PIPELINE_PREFIX}-{workspace}"
        return self.client.check_job_running(train_pipeline, job_id)

    def check_build_train_job_running(self, workspace, job_id):
        build_train_pipeline = f"{BUILD_TRAIN_PIPELINE_PREFIX}-{workspace}"
        return self.client.check_job_running(build_train_pipeline, job_id)
