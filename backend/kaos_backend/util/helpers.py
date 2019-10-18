import hashlib
import math
import os
import uuid
import zipfile
from distutils.dir_util import copy_tree
from io import BytesIO
from itertools import product
from tempfile import TemporaryDirectory
from zipfile import ZipFile, BadZipFile

from kaos_backend import get_resource
from kaos_backend.exceptions.exceptions import InvalidBundleError


def fix_string_length(s: str, n: int = 5):
    """
    Small utility to fix length of input string

    Args:
        s: input string
        n: desired fixed length of input string

    Returns:
        <shortened output string>

    """
    assert n > 0, "ZeroDivisionError - n must be greater than 0!"
    ind = math.ceil(len(s) / n)
    return s[::ind]


def build_hash(data_bytes: str):
    """
    Helper for building sha512 hash of byte data

    Args:
        data_bytes: raw bytes from data/source bundle

    Returns:
        <shortened hex response of hash function>

    """
    # create hash
    hash_sha512 = hashlib.sha512()
    hash_sha512.update(data_bytes)
    return fix_string_length(hash_sha512.hexdigest())


def product_dict(**kwargs):
    """
    Helper for determining hyperparams with product of dictionary keys/values

    Args:
        **kwargs: keys/values

    Returns:
        <dict with product of keys/values>

    """
    keys = kwargs.keys()
    values = kwargs.values()
    for instance in product(*values):
        yield dict(zip(keys, instance))


def remove_files_from_directory(directory, *args):
    """
    Helper function to remove sequence of filenames from directory

    Args:
        directory: base directory
        *args: sequence of filenames
    """
    args = set(args)
    for root, _, files in os.walk(directory):
        for f in files:
            if f in args:
                exclude_path = os.path.join(root, f)
                if os.path.exists(exclude_path):
                    os.remove(exclude_path)


class BundleDirectory(TemporaryDirectory):

    def __init__(self, data, suffix=None, prefix=None, dir=None):
        super(BundleDirectory, self).__init__(suffix, prefix, dir)
        self._data = data

    def __enter__(self):
        dirname = super(BundleDirectory, self).__enter__()
        try:

            ZipFile(BytesIO(self._data), 'r').extractall(dirname)

            self.remove_hidden_files(dirname)

        except BadZipFile as e:
            self.cleanup()
            raise InvalidBundleError("Bundle is malformed") from e

        return dirname

    @staticmethod
    def remove_hidden_files(dirname):
        for f in os.listdir(dirname):
            if os.path.isfile(os.path.join(dirname, f)) and f.startswith("."):
                os.remove(os.path.join(dirname, f))


class NotebookDirectory(BundleDirectory):

    def __init__(self, data=None, gpu=0, suffix=None, prefix=None, dir=None):
        super(NotebookDirectory, self).__init__(data, suffix, prefix, dir)
        self.data = data
        self.gpu = bool(gpu)

    def __enter__(self):
        if self.data:
            tmp = super(NotebookDirectory, self).__enter__()
        else:
            tmp = self.name
            # take the template and copy it to tmp
            notebook_res = get_resource('notebook-gpu' if self.gpu else 'notebook')
            copy_tree(notebook_res, tmp)
            self.remove_hidden_files(tmp)

        return tmp


class BundleHash(object):

    @staticmethod
    def hash(temp_dir, data_bytes):
        # create hash
        hash_hex = build_hash(data_bytes)

        # append hex to name -> move directory
        src = os.path.join(temp_dir, os.listdir(temp_dir)[0])
        dst = f"{src}:{hash_hex}"
        os.rename(src, dst)

        return dst


class TemporaryZipDirectory(TemporaryDirectory):

    def __init__(self, directory):
        super(TemporaryZipDirectory, self).__init__()
        self.directory = directory

    def __enter__(self):
        filename = str(uuid.uuid4()) + ".zip"
        full_path = os.path.join(self.name, filename)
        zip_f = zipfile.ZipFile(full_path, 'w', zipfile.ZIP_DEFLATED)
        zip_dir(self.directory, zip_f)
        zip_f.close()

        in_file = open(full_path, "rb")  # opening for [r]eading as [b]inary
        return in_file.read()


def zip_dir(path, zip_h):
    # ziph is zipfile handle
    abs_dirname = os.path.abspath(path)

    for root, dirs, files in os.walk(path):
        for f in files:
            abs_name = os.path.abspath(os.path.join(root, f))
            arc_name = abs_name[len(abs_dirname) + 1:]
            zip_h.write(abs_name, arc_name)


def copy_current_app_context(f):
    from flask.globals import _app_ctx_stack
    appctx = _app_ctx_stack.top

    def _(*args, **kwargs):
        with appctx:
            return f(*args, **kwargs)

    return _
