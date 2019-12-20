import os
import re

from flask import request
from kaos_backend.constants import MAX_CPU, MAX_GPU, MAX_MEMORY
from kaos_backend.exceptions.exceptions import InvalidBundleError, \
    MemoryRequestError, GPURequestError, CPURequestError, \
    AuthorizationError

SOURCE_URL = "https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#meaning-of-memory"

TO_BYTES = {
    "k": 10 ** 3,
    "M": 10 ** 6,
    "G": 10 ** 9,
    "T": 10 ** 12,
    "P": 10 ** 15,
    "Ki": 2 ** 10,
    "Mi": 2 ** 20,
    "Gi": 2 ** 30,
    "Ti": 2 ** 40,
    "Pi": 2 ** 50,
}


class BundleValidator:
    REQUIRED_INFERENCE_FILES = ["__init__.py",
                                "serve",
                                "web-requirements.txt"]

    REQUIRED_TRAINING_FILES = ["__init__.py",
                               "requirements.txt",
                               "train"]

    MODEL = "model"

    @classmethod
    def is_empty(cls, directory: str) -> bool:
        return all(len(files) == 0 for root, _, files in os.walk(directory))

    @classmethod
    def validate_empty(cls, directory):
        if cls.is_empty(directory):
            raise InvalidBundleError("Bundle must be non-empty")

    @classmethod
    def validate_model_directory(cls, dirs):
        if "model" not in dirs:
            raise InvalidBundleError("Missing model directory in source-code bundle")

    @classmethod
    def validate_dockerfile(cls, files):
        if "Dockerfile" not in files:
            raise InvalidBundleError("Missing Dockerfile in source-code bundle")

    @classmethod
    def validate_root_directory(cls, dirs):
        if len(dirs) > 1:
            raise InvalidBundleError("Too many directories in source-code bundle")
        elif len(dirs) == 0:
            raise InvalidBundleError("Missing root directory in source-code bundle")

    @classmethod
    def validate_file(cls, f, files):
        if f not in files:
            raise InvalidBundleError(f"Missing file {f} in model directory of source-code bundle")

    @classmethod
    def validate_bundle_structure(cls, directory, req_files):
        cls.validate_empty(directory)
        bundle_root, model_dir = None, None
        for root, dirs, files in os.walk(directory):

            if root == directory:
                cls.validate_root_directory(dirs)
                bundle_root = os.path.join(root, dirs[0])

            if bundle_root:
                if root == bundle_root:
                    cls.validate_dockerfile(files)
                    cls.validate_model_directory(dirs)
                    model_dir = os.path.join(bundle_root, cls.MODEL)

                if root == model_dir:
                    for f in req_files:
                        cls.validate_file(f, files)

    @classmethod
    def validate_inference_bundle_structure(cls, directory: str):
        req_files = cls.REQUIRED_INFERENCE_FILES
        cls.validate_bundle_structure(directory, req_files)

    @classmethod
    def validate_notebook_bundle_structure(cls, directory):
        cls.validate_bundle_structure(directory, [])

    @classmethod
    def validate_train_bundle_structure(cls, directory):
        req_files = cls.REQUIRED_TRAINING_FILES
        cls.validate_bundle_structure(directory, req_files)


def validate_cpu_request(cpu):
    if cpu and MAX_CPU:
        cpu = float(cpu)
        if cpu > MAX_CPU:
            raise CPURequestError(f" CPU request {cpu} too high. Maximum allowed is {MAX_CPU}.")


def validate_memory_request(memory):
    validate_memory_string(memory)

    if MAX_MEMORY and memory:
        memory_gb = f"{MAX_MEMORY}Gi"
        memory_request = memory_to_bytes(memory)
        memory_limit = memory_to_bytes(memory_gb)
        if memory_request > memory_limit:
            raise MemoryRequestError(f'Memory request {memory} too high. Maximum allowed is {memory_gb}.')


def memory_to_bytes(memory):
    for k, v in TO_BYTES.items():
        if memory.endswith(k):
            return v * float(memory.replace(k, ""))
    return float(memory)


def validate_memory_string(memory):
    """
    Validates the input memory string according to the SI memory suffixes defined within kubernetes

    https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/#meaning-of-memory

    Args:
        memory (str): requested memory

    """
    if memory:
        p = re.compile("^([+-]?[0123456789.]+)([eiEKMGTP]*[-+]?[0123456789]*)$")
        m = re.match(p, memory)
        if not m:
            raise MemoryRequestError(f'Incorrect memory request {memory}\n\nPlease check memory specs: {SOURCE_URL}')


def validate_gpu_request(gpu):
    if gpu > MAX_GPU:
        raise GPURequestError("GPUs are not enabled")


def validate_resources(function):
    """
    Validation of resource requests
    """

    def wrapper(*args, **kwargs):
        cpu = kwargs["cpu"]
        memory = kwargs["memory"]
        gpu = kwargs["gpu"]
        validate_cpu_request(cpu)
        validate_gpu_request(gpu)
        validate_memory_request(memory)
        return function(*args, **kwargs)

    return wrapper


def auth_required(function):
    """
    Authenticate the token in the authorization header
    """

    def wrapper(*args, **kwargs):
        token = os.getenv("TOKEN")
        if 'X-Token' not in request.headers:
            raise AuthorizationError("Authorization header not present in the request")

        req_token = request.headers['X-Token']

        if req_token != token:
            raise AuthorizationError("Unauthorized Token")
        return function(*args, **kwargs)

    wrapper.__name__ = function.__name__
    return wrapper
