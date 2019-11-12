import os
from concurrent.futures import ThreadPoolExecutor

import bitstring
import python_pachyderm.proto.pfs.pfs_pb2 as pfs_proto
import urllib3
from cgroupspy import trees
from flask import current_app as app
from kaos_backend.exceptions.exceptions import JobNotFoundError, PipelineNotFoundError, PipelineInStandby
from kaos_backend.util.error_handling import handle_pachyderm_error
from kaos_backend.util.protobuf import proto_to_dict
from psutil import virtual_memory
from python_pachyderm import Client
from python_pachyderm.proto.pps import pps_pb2 as proto
from urllib3 import PoolManager

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class PachydermClient:
    """
    This is kaos' client layer for Pachyderm.

    Abstracts low-level workspace-agnostic definitions and operations in Pachyderm and provides error handling.
    """

    GPU_TYPE = "nvidia.com/gpu"

    def __init__(self, pclient: Client):
        """
        PachydermClient constructor.

        Args:
            pclient (Client): Pachyderm System client
        """
        self.pclient = pclient
        self.pool = PoolManager()
        # TODO: expose
        self.max_workers = 20
        try:
            self.memory_limit = trees.Tree().get_node_by_path("/memory/").controller.limit_in_bytes
        except FileNotFoundError:
            # cgroups not found, probably running on local machine
            self.memory_limit = virtual_memory().available
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)

    @handle_pachyderm_error
    def create_pipeline(self,
                        name: str,
                        image: str,
                        commands: list,
                        description: str,
                        pfs_input: proto.Input,
                        standby=False,
                        parallelism=1,
                        output_branch='master',
                        service=None,
                        env=None,
                        update=False,
                        reprocess=False,
                        datum_tries=1,
                        cpu: float = None,
                        memory: str = None,
                        gpu: int = 0):
        app.logger.debug("@%s: create pipeline %s", PachydermClient.__name__, name)
        app.logger.debug("@%s: cpu %s gpu %s memory %s", PachydermClient.__name__, cpu, gpu, memory)

        transform = proto.Transform(cmd=["/bin/bash"],
                                    stdin=["set -e"] + commands,
                                    env=env,
                                    image=image)

        resource_limits, resource_requests = self.define_resources(cpu, gpu, memory)

        return self.pclient.create_pipeline(
            name,
            description=description,
            transform=transform,
            enable_stats=True,
            parallelism_spec=proto.ParallelismSpec(constant=parallelism),
            input=pfs_input,
            standby=standby,
            output_branch=output_branch,
            service=service,
            update=update,
            reprocess=reprocess,
            datum_tries=datum_tries,
            resource_requests=resource_requests,
            resource_limits=resource_limits)

    def define_resources(self, cpu, gpu, memory):
        cpu = float(cpu) if cpu else cpu

        resource_limits, resource_requests = [None] * 2
        gpu_spec = proto.GPUSpec(type=self.GPU_TYPE, number=gpu)

        if cpu and memory and gpu:
            resource_requests = proto.ResourceSpec(cpu=cpu, memory=memory)
            resource_limits = proto.ResourceSpec(cpu=cpu, memory=memory, gpu=gpu_spec)
        elif cpu and memory:
            resource_requests = proto.ResourceSpec(cpu=cpu, memory=memory)
            resource_limits = resource_requests
        elif cpu and gpu:
            resource_requests = proto.ResourceSpec(cpu=cpu)
            resource_limits = proto.ResourceSpec(cpu=cpu, gpu=gpu_spec)
        elif memory and gpu:
            resource_requests = proto.ResourceSpec(memory=memory)
            resource_limits = proto.ResourceSpec(memory=memory, gpu=gpu_spec)
        elif cpu:
            resource_requests = proto.ResourceSpec(cpu=cpu)
            resource_limits = resource_requests
        elif memory:
            resource_requests = proto.ResourceSpec(memory=memory)
            resource_limits = resource_requests
        elif gpu:
            resource_requests = None
            resource_limits = proto.ResourceSpec(gpu=gpu_spec)

        return resource_limits, resource_requests

    @handle_pachyderm_error
    def create_repo(self, repo: str, desc=None):
        app.logger.debug("@%s: creating repo %s", PachydermClient.__name__, repo)

        # make new repo (if needed)
        repos = [r.repo.name for r in self.pclient.list_repo()]
        if repo not in repos:
            app.logger.debug("@%s: repo does not exists %s", PachydermClient.__name__, repo)
            self.pclient.create_repo(repo, description=desc)
            self.pclient.create_branch(repo, "master")
        else:
            app.logger.debug("@%s: repo exists %s", PachydermClient.__name__, repo)

    @proto_to_dict
    def kill_build_train_pipeline(self):
        pass

    @proto_to_dict
    def kill_train_pipeline(self):
        pass

    @proto_to_dict
    def kill_build_serve_pipeline(self):
        pass

    @proto_to_dict
    def kill_serve_pipeline(self):
        pass

    @proto_to_dict
    def create_notebook_service_pipeline(self):
        pass

    @proto_to_dict
    def kill_notebook_service_pipeline(self):
        pass

    @handle_pachyderm_error
    def put_blobs(self, repo: str, blobs_list: list, desc=None):
        app.logger.debug("@%s: put blobs in repository %s", PachydermClient.__name__, repo)
        # keep single commit for input data
        with self.pclient.commit(repo, 'master', description=desc) as c:
            for blob in blobs_list:
                self.pclient.put_file_bytes(c, blob['path'], blob['blob'], overwrite_index=0)
            commit_id = c.id

        return commit_id

    @handle_pachyderm_error
    def put_blob(self, repo: str, path, blob, split_by_lines=None, desc=None):
        app.logger.debug("@%s: put blob in repository %s", PachydermClient.__name__, repo)
        with self.pclient.commit(repo, 'master', description=desc) as c:
            delimiter = "LINE" if split_by_lines else None
            app.logger.debug("putting blob split: %s; commit: %s", split_by_lines, c)
            self.pclient.put_file_bytes(c, path, blob,
                                        overwrite_index=0, delimiter=delimiter)

    @handle_pachyderm_error
    def put_dir_base(self, repo: str, path: str, upload_f: callable, desc=None):
        app.logger.debug("@%s: put directory in repository %s at path %s", PachydermClient.__name__, repo, path)
        files = [pathname
                 for paths in map(lambda x: [os.path.join(x[0], f) for f in x[2]],
                                  os.walk(path, followlinks=True))
                 for pathname in paths]
        # keep single commit for input data
        with self.pclient.commit(repo, 'master', description=desc) as c:
            for file in files:
                if os.stat(file).st_size != 0:
                    upload_f(path, c, file)
            commit_id = c.id
        return commit_id

    @handle_pachyderm_error
    def put_dir(self, repo: str, source_path: str, desc=None, prefix: str = ""):
        def upload_files(path: str, commit, file: str):
            commit_id = commit.id
            repo_name = commit.repo.name
            app.logger.debug("@%s: upload files at path %s with commit id %s on repo %s",
                             PachydermClient.__name__, path, commit_id, repo_name)
            self.pclient.put_file_bytes(commit, os.path.join(prefix, os.path.relpath(file, path)),
                                        open(file, "rb").read(),
                                        overwrite_index=0)

        return self.put_dir_base(repo, source_path, upload_files, desc)

    @handle_pachyderm_error
    def get_dir(self, repo: str, commit: str, path: str, out_dir=os.getcwd(), remove_prefix=False):
        app.logger.debug("@%s: get dir from repo %s with commit id %s", PachydermClient.__name__, repo, commit)
        objs = self.list_file(f"{repo}/{commit}", path=path, recursive=True)
        for obj in objs:
            obj_path = obj.file.path
            x = self.pclient.get_file(f"{repo}/{commit}",
                                      path=obj_path)
            if remove_prefix:
                obj_path = os.path.relpath(obj_path, path)
            # TODO -> attach <output_branch> when saving model (for consistency)
            out_file_path = os.path.join(out_dir, obj_path.strip('/'))
            os.makedirs(os.path.dirname(out_file_path), exist_ok=True)
            with open(out_file_path, 'wb') as dst:
                for i in x:
                    dst.write(i)

    @handle_pachyderm_error
    def get_blob(self, repo: str, commit: str, path: str):
        app.logger.debug("@%s: get blob from repo %s at path %s with commit id %s", PachydermClient.__name__, repo,
                         path, commit)

        file = self.pclient.get_file(f"{repo}/{commit}",
                                     path=path)
        stream = bitstring.BitStream()

        for chunk in file:
            stream.append(chunk)

        return stream.bytes

    @handle_pachyderm_error
    def list_pipelines(self):
        app.logger.debug("@%s: list pipelines", PachydermClient.__name__)
        return [r.pipeline.name for r in self.pclient.list_pipeline().pipeline_info]

    @handle_pachyderm_error
    def list_repos(self):
        app.logger.debug("@%s: list repo", PachydermClient.__name__)
        return [r.repo.name for r in self.pclient.list_repo()]

    @handle_pachyderm_error
    def check_repo_empty(self, repo: str):
        app.logger.debug("@%s: check repo %s is empty", PachydermClient.__name__, repo)
        return self.pclient.inspect_repo(repo).size_bytes == 0

    @handle_pachyderm_error
    def inspect_pipeline(self, pipeline: str):
        app.logger.debug("@%s: inspect pipeline %s", PachydermClient.__name__, pipeline)
        return self.pclient.inspect_pipeline(pipeline)

    @handle_pachyderm_error
    def check_pipeline_exists(self, pipeline: str):
        app.logger.debug("@%s: check pipeline %s exists", PachydermClient.__name__, pipeline)
        return pipeline in self.list_pipelines()

    @handle_pachyderm_error
    def check_repo_exists(self, repo: str):
        app.logger.debug("@%s: check repo %s exists", PachydermClient.__name__, repo)
        repos = [r.repo.name for r in self.pclient.list_repo()]
        return repo in repos

    @handle_pachyderm_error
    def check_branch_exists(self, repo: str, branch: str):
        app.logger.debug("@%s: check branch %s exists in %s", PachydermClient.__name__, branch, repo)
        branches = [r.name for r in self.pclient.list_branch(repo)]
        return branch in branches

    @handle_pachyderm_error
    def check_job_running(self, pipeline_name: str, job_id: str):
        app.logger.debug("@%s: check job %s exists from %s", PachydermClient.__name__, job_id, pipeline_name)
        jobs = [(r.job.id, r.state) for r in self.pclient.list_job(pipeline_name, history=-1)]
        app.logger.debug(jobs)
        return (job_id, 0) in jobs or (job_id, 1) in jobs

    @handle_pachyderm_error
    def check_job_exists(self, pipeline_name: str, job_id: str):
        app.logger.debug("@%s: check job %s exists from %s", PachydermClient.__name__, job_id, pipeline_name)
        jobs = [r.job.id for r in self.pclient.list_job(pipeline_name, history=-1)]
        return job_id in jobs

    @handle_pachyderm_error
    def list_file(self, commit: str, path: str, recursive=False, history=-1):
        app.logger.debug("@%s: list file from commit %s in path %s", PachydermClient.__name__, commit, path)
        file_infos = list(self.pclient.list_file(commit, path, history=history))

        if recursive:
            dirs = [f for f in file_infos if f.file_type == pfs_proto.DIR]
            files = [f for f in file_infos if f.file_type == pfs_proto.FILE]
            return sum([self.list_file(commit, d.file.path, recursive) for d in dirs], files)

        return file_infos

    @handle_pachyderm_error
    def inspect_file(self, commit: str, path: str):
        app.logger.debug("@%s: list file from commit %s in path %s", PachydermClient.__name__, commit, path)
        return self.pclient.inspect_file(commit=commit, path=path)

    @handle_pachyderm_error
    def list_commit(self, repo: str, to_commit=None):
        app.logger.debug("@%s: list commit %s in repo %s", PachydermClient.__name__, to_commit, repo)
        return self.pclient.list_commit(repo_name=repo, to_commit=to_commit)

    @handle_pachyderm_error
    def inspect_commit(self, commit: str):
        app.logger.debug("@%s: inspect commit %s", PachydermClient.__name__, commit)
        return self.pclient.inspect_commit(commit)

    @handle_pachyderm_error
    def inspect_job(self, job_id: str):
        app.logger.debug("@%s: inspect job %s", PachydermClient.__name__, job_id)
        return self.pclient.inspect_job(job_id=job_id)

    @handle_pachyderm_error
    def delete_repo(self, repo_name: str):
        app.logger.debug("@%s: delete repo %s", PachydermClient.__name__, repo_name)
        return self.pclient.delete_repo(repo_name, force=True)

    @handle_pachyderm_error
    def delete_pipeline(self, pipeline_name):
        app.logger.debug("@%s: delete pipeline %s", PachydermClient.__name__, pipeline_name)
        return self.pclient.delete_pipeline(pipeline_name)

    @handle_pachyderm_error
    def delete_job(self, pipeline_name, job_id):
        app.logger.debug("@%s: delete job %s", PachydermClient.__name__, job_id)

        # ensure job and pipeline exist!
        if not self.check_pipeline_exists(pipeline_name):
            raise PipelineNotFoundError(pipeline_name)

        if not self.check_job_exists(pipeline_name, job_id):
            raise JobNotFoundError(job_id)

        return self.pclient.delete_job(job_id)

    @handle_pachyderm_error
    def get_job_logs(self, pipeline_name, job_id):
        app.logger.debug("@%s: get logs from job %s", PachydermClient.__name__, job_id)

        # ensure pipeline exists!
        if not self.check_pipeline_exists(pipeline_name):
            raise PipelineNotFoundError(pipeline_name)

        # ensure job exists!
        if not self.check_job_exists(pipeline_name, job_id):
            raise JobNotFoundError(job_id)

        # ensure job is completed!
        if not self.inspect_job(job_id).state == 3:
            app.logger.debug("@%s: job %s not complete - using pipeline logs!", PachydermClient.__name__, job_id)
            return self.get_pipeline_logs(pipeline_name)
        else:
            return self.pclient.get_job_logs(job_id=job_id)

    @handle_pachyderm_error
    def get_pipeline_logs(self, pipeline_name):
        app.logger.debug("@%s: get logs from pipeline %s", PachydermClient.__name__, pipeline_name)

        # ensure pipeline exists!
        if not self.check_pipeline_exists(pipeline_name):
            raise PipelineNotFoundError(pipeline_name)

        # ensure pipeline is NOT in standby
        if self.inspect_pipeline(pipeline_name).state == 5:
            raise PipelineInStandby(pipeline_name)

        return self.pclient.get_pipeline_logs(pipeline_name=pipeline_name)

    @handle_pachyderm_error
    def get_jobs(self, pipeline_name: str, history=-1):
        app.logger.debug("@%s: list jobs from pipeline %s", PachydermClient.__name__, pipeline_name)
        job_iterator = self.pclient.list_job(pipeline_name=pipeline_name, history=history)
        return [job for job in job_iterator]

    @handle_pachyderm_error
    def get_job_info(self, job_id: str):
        app.logger.debug("@%s: inspect jobs from job %s", PachydermClient.__name__, job_id)
        return self.pclient.inspect_job(job_id)

    @handle_pachyderm_error
    def list_datum(self, job_id):
        app.logger.debug("@%s: list datum by job %s", PachydermClient.__name__, job_id)
        return [datum for datum in self.pclient.list_datum(job_id)]

    @handle_pachyderm_error
    def delete_all(self):
        app.logger.debug("@%s: delete all", PachydermClient.__name__)
        self.pclient.delete_all()
        self.pclient.delete_all()
