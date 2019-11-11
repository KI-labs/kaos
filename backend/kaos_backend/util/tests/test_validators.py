import os
import tempfile
from tempfile import TemporaryDirectory

import pytest
from kaos_backend.exceptions.exceptions import InvalidBundleError
from kaos_backend.util.validators import BundleValidator

"""
Utility functions
"""


def create_file(path):
    temp = open(path, 'w+b')
    temp.close()
    return temp


def remove_el(l, el):
    ll = l[:]
    ll.remove(el)
    return ll


"""
Constants
"""
REQ_INFERENCE_FILES = BundleValidator.REQUIRED_INFERENCE_FILES
REQ_TRAINING_FILES = BundleValidator.REQUIRED_TRAINING_FILES

inference_test_cases = [(remove_el(REQ_INFERENCE_FILES, f), f) for f in REQ_INFERENCE_FILES]
notebook_test_cases = [(remove_el([], f), f) for f in []]
training_test_cases = [(remove_el(REQ_TRAINING_FILES, f), f) for f in REQ_TRAINING_FILES]
"""
Test Cases
"""


def test_is_empty():
    with TemporaryDirectory() as temp_dir:
        assert BundleValidator.is_empty(temp_dir) is True


def test_is_not_empty():
    with TemporaryDirectory() as temp_dir:
        temp = tempfile.NamedTemporaryFile(dir=temp_dir, delete=True)
        assert BundleValidator.is_empty(temp_dir) is False
        temp.close()


def test_validate_bundle_structure_is_empty():
    with pytest.raises(InvalidBundleError, match="Bundle must be non-empty"):
        with TemporaryDirectory() as temp_dir:
            BundleValidator.validate_bundle_structure(temp_dir, [])


def test_validate_bundle_structure_missing_root_directory():
    with pytest.raises(InvalidBundleError, match="Missing root directory in source-code bundle"):
        with TemporaryDirectory() as temp_dir:
            # temp file to avoid empty file exception
            temp = tempfile.NamedTemporaryFile(dir=temp_dir, delete=True)
            BundleValidator.validate_bundle_structure(temp_dir, [])
            temp.close()


def test_validate_bundle_structure_too_many_directories():
    with pytest.raises(InvalidBundleError, match="Too many directories in source-code bundle"):
        with TemporaryDirectory() as temp_dir:
            # temp file to avoid empty file exception
            temp = tempfile.NamedTemporaryFile(dir=temp_dir, delete=True)
            tempfile.mkdtemp(dir=temp_dir)
            tempfile.mkdtemp(dir=temp_dir)

            BundleValidator.validate_bundle_structure(temp_dir, [])
            temp.close()


def test_validate_bundle_structure_missing_dockerfile_in_directory():
    with pytest.raises(InvalidBundleError, match="Missing Dockerfile in source-code bundle"):
        with TemporaryDirectory() as temp_dir:
            # temp file to avoid empty file exception
            temp = tempfile.NamedTemporaryFile(dir=temp_dir, delete=True)
            tempfile.mkdtemp(dir=temp_dir)

            BundleValidator.validate_bundle_structure(temp_dir, [])
            temp.close()

def test_validate_bundle_structure_missing_model_directory():
    with pytest.raises(InvalidBundleError, match=""):
        with TemporaryDirectory() as temp_dir:
            base_dir = tempfile.mkdtemp(dir=temp_dir)
            filename = os.path.join(base_dir, "Dockerfile")
            create_file(filename)
            BundleValidator.validate_bundle_structure(temp_dir, [])

def test_validate_bundle_structure_missing_shebang_line_in_train():
    with pytest.raises(InvalidBundleError, match="The train file cannot be executed. \n"
                                                 "Please add the line '#!/usr/bin/xenv python3' "
                                                 "in the beginning of the train file to make it executable"):
        with TemporaryDirectory() as temp_dir:
            base_dir = tempfile.mkdtemp(dir=temp_dir)
            train_file = os.path.join(base_dir, "model", "train")
            create_file(train_file)
            BundleValidator.validate_bundle_structure(temp_dir, [])

@pytest.mark.parametrize("files_include,file_exclude", inference_test_cases)
def test_validate_inference_bundle_structure_missing_some_file(files_include, file_exclude):
    with pytest.raises(InvalidBundleError,
                       match=f"Missing file {file_exclude} in model directory of source-code bundle"):
        with TemporaryDirectory() as temp_dir:
            base_dir = tempfile.mkdtemp(dir=temp_dir)
            filename = os.path.join(base_dir, "Dockerfile")
            create_file(filename)

            model_dir = os.path.join(base_dir, "model")
            os.mkdir(model_dir)
            for f in files_include:
                create_file(os.path.join(model_dir, f))

            BundleValidator.validate_inference_bundle_structure(temp_dir)


@pytest.mark.parametrize("files_include,file_exclude", notebook_test_cases)
def test_validate_notebook_bundle_structure_missing_some_file(files_include, file_exclude):
    with pytest.raises(InvalidBundleError,
                       match=f"Missing file {file_exclude} in model directory of source-code bundle"):
        with TemporaryDirectory() as temp_dir:
            base_dir = tempfile.mkdtemp(dir=temp_dir)
            filename = os.path.join(base_dir, "Dockerfile")
            create_file(filename)

            model_dir = os.path.join(base_dir, "model")
            os.mkdir(model_dir)
            for f in files_include:
                create_file(os.path.join(model_dir, f))

            BundleValidator.validate_notebook_bundle_structure(temp_dir)


@pytest.mark.parametrize("files_include,file_exclude", training_test_cases)
def test_validate_train_bundle_structure_missing_some_file(files_include, file_exclude):
    with pytest.raises(InvalidBundleError,
                       match=f"Missing file {file_exclude} in model directory of source-code bundle"):
        with TemporaryDirectory() as temp_dir:
            base_dir = tempfile.mkdtemp(dir=temp_dir)
            filename = os.path.join(base_dir, "Dockerfile")
            create_file(filename)

            model_dir = os.path.join(base_dir, "model")
            os.mkdir(model_dir)
            for f in files_include:
                create_file(os.path.join(model_dir, f))

            BundleValidator.validate_train_bundle_structure(temp_dir)
