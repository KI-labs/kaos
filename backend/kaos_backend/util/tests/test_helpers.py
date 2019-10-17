import io
import os
import shutil
import zipfile
from tempfile import TemporaryDirectory, NamedTemporaryFile

import pytest
from kaos_backend.exceptions.exceptions import InvalidBundleError
from kaos_backend.util.helpers import BundleDirectory, NotebookDirectory, TemporaryZipDirectory
from kaos_backend.util.tests import create_zip, create_zip_with_ds_store
from kaos_backend.util.utility import get_dir_and_files


def test_malformed_bundle():
    with pytest.raises(InvalidBundleError, match="Bundle is malformed"):
        with BundleDirectory(b'something'):
            pass


def test_single_file_bundle():
    bytes_content, f, t, zip_file_name = create_zip()

    with BundleDirectory(bytes_content) as tmp:
        assert os.path.exists(tmp) is True

    f.close()
    t.cleanup()
    os.remove(zip_file_name)


def test_single_ds_store_bundle():
    bytes_content, t, zip_file_name = create_zip_with_ds_store()

    with BundleDirectory(bytes_content) as tmp:

        assert os.path.exists(tmp) is True
        assert os.path.exists(os.path.join(tmp, ".DS_Store")) is False

    t.cleanup()
    os.remove(zip_file_name)


def test_no_data_notebook_directory_copy_template():
    # this test verifies that the template notebook gets copied to the bundle
    with NotebookDirectory() as tmp:
        dir_files = get_dir_and_files(tmp)

        assert 'Dockerfile' in dir_files
        assert 'base' in dir_files
        assert 'model' in dir_files
        assert 'requirements.txt' in dir_files


def test_simple_data_notebook_directory():
    bytes_content, f, t, zip_file_name = create_zip()

    with NotebookDirectory(data=bytes_content) as tmp:
        assert os.path.exists(tmp) is True
        assert len(os.listdir(tmp)) > 0

    t.cleanup()
    os.remove(zip_file_name)


def test_temporary_zip_directory():
    t = TemporaryDirectory()
    f = NamedTemporaryFile(dir=t.name, delete=True)
    f.file.write(b'01')

    z = TemporaryZipDirectory(t.name)
    with z as bytes:
        assert bytes is not None
        zf = zipfile.ZipFile(io.BytesIO(bytes))
        zf.extractall("./tests")
        assert os.path.exists("./tests")
        assert os.path.exists(os.path.join("./tests", f.name))
        shutil.rmtree("./tests")

    t.cleanup()
    assert not os.path.exists(z.name)
