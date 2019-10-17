class ApplicationError(Exception):
    def __init__(self, message):
        self.message = message


class JobServiceError(ApplicationError):
    pass


class PachydermError(ApplicationError):
    pass


class JobNotFoundError(JobServiceError):
    def __init__(self, job_id):
        super().__init__(f"There is no job with id: {job_id}")


class JobNotRunningError(JobServiceError):
    def __init__(self, job_id):
        super().__init__(f"Job is not running, id: {job_id}")


class ModelNotFoundError(JobServiceError):
    def __init__(self, model_id):
        super().__init__(f"There is no model with id: {model_id}")


class AlienProvenanceError(JobServiceError):
    def __init__(self):
        super().__init__(f"Unable to determine provenance with external model")


class IncompleteDatumError(JobServiceError):
    def __init__(self, job_id):
        super().__init__(f"Incomplete datum for job: {job_id}")


class NotebookAlreadyExistsError(JobServiceError):
    def __init__(self, pipeline):
        super().__init__(f"Notebook already exists: {pipeline}")


class PipelineNotFoundError(JobServiceError):
    def __init__(self, pipeline):
        super().__init__(f"Pipeline {pipeline} not found")


class PipelineInStandby(JobServiceError):
    def __init__(self, pipeline):
        super().__init__(f"The pipeline is currently in standby: {pipeline}")


class MetricNotFound(JobServiceError):
    def __init__(self, metric_name):
        super().__init__(f"Metric {metric_name} not found")


class UnfinishedCommitError(PachydermError):
    def __init__(self, commit_id):
        super().__init__(f"Tried accessing repo with a pending commit {commit_id}")
        self.commit_id = commit_id


class CommitNotFoundError(PachydermError):
    def __init__(self, commit_id):
        super().__init__(f"Tried to access commit that does not exist: {commit_id}")
        self.commit_id = commit_id


class BadRequestMethodError(Exception):
    def __init__(self, message):
        super().__init__(message)


class PageError(Exception):
    def __init__(self, message):
        super().__init__(message)


class InvalidBundleError(ApplicationError):
    pass


class CPURequestError(ApplicationError):
    pass


class GPURequestError(ApplicationError):
    pass


class MemoryRequestError(ApplicationError):
    pass
