from kaos_backend.exceptions.exceptions import BadRequestMethodError, NotebookAlreadyExistsError, JobNotFoundError, \
    ModelNotFoundError, PipelineInStandby, PipelineNotFoundError, MetricNotFound, \
    CommitNotFoundError, IncompleteDatumError, UnfinishedCommitError, PachydermError, JobNotRunningError, \
    PageError, InvalidBundleError, AlienProvenanceError, GPURequestError, MemoryRequestError, CPURequestError, \
    AuthorizationError

from kaos_model.api import Error


def make_error_response(status_code, error_code, message):
    return Error(error_code=error_code, message=message).to_json(), status_code


def register_application_exception(app):
    @app.errorhandler(BadRequestMethodError)
    def handle_bad_request_error(error):
        return make_error_response(400, error_code="BAD_REQUEST", message=error.message)

    @app.errorhandler(InvalidBundleError)
    def handle_invalid_bundle_error(error):
        return make_error_response(400, error_code="INVALID_BUNDLE", message=error.message)

    @app.errorhandler(PageError)
    def handle_page_error(error):
        return make_error_response(400, error_code="PAGE_ERROR", message=error.message)

    @app.errorhandler(NotebookAlreadyExistsError)
    def handle_notebook_already_exists_error(error):
        return make_error_response(409, error_code="NOTEBOOK_EXISTS", message=error.message)

    @app.errorhandler(JobNotFoundError)
    def handle_job_not_found_error(error):
        return make_error_response(404, error_code="JOB_NOT_FOUND", message=error.message)

    @app.errorhandler(JobNotRunningError)
    def handle_job_not_running_error(error):
        return make_error_response(400, error_code="JOB_NOT_RUNNING", message=error.message)

    @app.errorhandler(ModelNotFoundError)
    def handle_model_not_found_error(error):
        return make_error_response(404, error_code="MODEL_NOT_FOUND", message=error.message)

    @app.errorhandler(GPURequestError)
    def handle_gpu_request_error(error):
        return make_error_response(404, error_code="GPU_REQUEST_ERROR", message=error.message)

    @app.errorhandler(MemoryRequestError)
    def handle_memory_request_error(error):
        return make_error_response(404, error_code="MEMORY_REQUEST_ERROR", message=error.message)

    @app.errorhandler(CPURequestError)
    def handle_cpu_request_error(error):
        return make_error_response(404, error_code="CPU_REQUEST_ERROR", message=error.message)

    @app.errorhandler(PipelineNotFoundError)
    def handle_pipeline_not_found_error(error):
        return make_error_response(404, error_code="PIPELINE_NOT_FOUND", message=error.message)

    @app.errorhandler(MetricNotFound)
    def handle_metric_not_found_error(error):
        return make_error_response(404, error_code="METRIC_NOT_FOUND", message=error.message)

    @app.errorhandler(AlienProvenanceError)
    def handle_alien_provenance_error(error):
        return make_error_response(404, error_code="ALIEN_PROVENANCE_ERROR", message=error.message)

    @app.errorhandler(CommitNotFoundError)
    def handle_commit_not_found_error(error):
        return make_error_response(404, error_code="COMMIT_NOT_FOUND", message=error.message)

    @app.errorhandler(PachydermError)
    def handle_pachyderm_error(error):
        return make_error_response(500, error_code="PACHYDERM_ERROR", message=error.message)

    @app.errorhandler(IncompleteDatumError)
    def handle_incomplete_datum_error(error):
        return make_error_response(500, error_code="INCOMPLETE_DATUM_ERROR", message=error.message)

    @app.errorhandler(PipelineInStandby)
    def handle_pipeline_in_standby_error(error):
        return make_error_response(500, error_code="PIPELINE_IN_STANDBY", message=error.message)

    @app.errorhandler(UnfinishedCommitError)
    def handle_unfinished_commit_error(error):
        return make_error_response(500, error_code="UNFINISHED_COMMIT", message=error.message)

    @app.errorhandler(AuthorizationError)
    def handle_authorization_error(error):
        return make_error_response(401, error_code="AUTHORIZATION_FAILURE", message=error.message)
