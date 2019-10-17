import os
from tempfile import TemporaryDirectory

from kaos_backend.clients.pachyderm import PachydermClient
from kaos_backend.services.job_service import JobService
from kaos_backend.util.tests import create_zip_file
from kaos_backend.util.validators import BundleValidator
from python_pachyderm import PpsClient, PfsClient


def t_any(cls):
    """
        Verifies if input is of same class
    """
    class AnyClass(cls):
        def __eq__(self, other):
            return True

    return AnyClass()


def create_job_service(mocker, workspaces=None):
    """
    Creates a Mock job Service

    Return:
         service: `kaos_backend.services.JobService`

    """
    client = PachydermClient(PpsClient(), PfsClient())
    service = JobService(client)

    def check_pipeline_exists_mock(pipeline_name):
        return pipeline_name.split('-')[-1] in workspaces

    client.check_pipeline_exists = mocker.Mock(side_effect=check_pipeline_exists_mock)

    return service


def create_test_file(dirname, filename):
    f = open(os.path.join(dirname, filename), "w")
    f.write("this is fake")
    f.close()
    return f


def create_bundle_zip(files):
    tempdir = TemporaryDirectory()
    root_dir = tempdir.name

    main_dir = os.path.join(root_dir, "test")
    os.mkdir(main_dir)

    model_dir = os.path.join(main_dir, BundleValidator.MODEL)
    os.mkdir(model_dir)

    filename = "Dockerfile"
    create_test_file(main_dir, filename)

    for f in files:
        create_test_file(model_dir, f)

    zip_filename = create_zip_file(root_dir)
    with open(zip_filename, 'rb') as file_data:
        bytes_content = file_data.read()

    return bytes_content, tempdir, zip_filename


def create_train_zip():
    return create_bundle_zip(BundleValidator.REQUIRED_TRAINING_FILES)


def create_inference_zip():
    return create_bundle_zip(BundleValidator.REQUIRED_INFERENCE_FILES)
