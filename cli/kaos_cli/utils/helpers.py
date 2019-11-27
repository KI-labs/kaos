import io
import os
import shlex
import zipfile
from subprocess import Popen, PIPE
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import requests
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
from tqdm import tqdm


def build_dir(*path_parts):
    """
    Utility for building and creating directory

    Args:
        path_parts (str): parts of directory for building

    Returns:
        out_dir (str): created local path

    """
    out_dir = os.path.join(*path_parts)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    return out_dir


def verbose_run(verbose, cmd):
    """
    Function for running a subprocess call with streamed verbose output
    Args:
        verbose (boolean): output on stdout
        cmd (str): shell cmd to execute
    """
    process = Popen(cmd, stdout=PIPE, shell=True)

    while True:
        output = process.stdout.readline()
        if process.poll() is not None:
            break
        if verbose:
            print(output.rstrip().decode("ascii"))
    rc = process.poll()
    return rc, process.stdout, process.stderr


def run_cmd(cmd):
    """
    Basic function for running a subprocess call and returning response
    Args:
        cmd (str): shell command to execute
    Returns:
        exitcode (str): exit code from command
        out (str): response
        err (str): error (if any)
    """
    args = shlex.split(cmd)
    proc = Popen(args, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()
    exitcode = proc.returncode
    return exitcode, out, err


def walk(folder):
    """
        Walk through each files in a directory
    """
    for root, dirs, files in os.walk(folder):
        for filename in files:
            yield os.path.abspath(os.path.join(root, filename))


def upload_with_progress_bar(data, url, kwargs, label=None, token=None):
    """
    Uses multipart data to show progress of upload to the user.
    Requires request.files['data'].read() instead of request.data on the backend site.
    :param data: path to file to upload
    :param url: target url
    :param kwargs: additional args for the post request
    :param label: label of progress bar
    :param token: token to authorize the request
    :return: response from server
    """
    encoder = MultipartEncoder({'data': ('data', data, 'text/plain')})

    with tqdm(desc=label,
              total=encoder.len,
              disable=not label,
              dynamic_ncols=True,
              unit='B',
              unit_scale=True,
              unit_divisor=1024) as bar:
        multipart_monitor = MultipartEncoderMonitor(encoder, lambda monitor: bar.update(monitor.bytes_read - bar.n))
        r = requests.post(url,
                          data=multipart_monitor,
                          headers={'Content-Type': multipart_monitor.content_type, 'Authorization': f'Bearer {token}'},
                          params=kwargs)

    return r


class Compressor(TemporaryDirectory):
    """
        Helper Class that compresses a source directory into a TemporaryDirectory
    """

    def __init__(self, filename, source_path, label):
        super(Compressor, self).__init__()
        self.zip_filename = filename
        self.source_path = source_path
        self.label = label

    def __enter__(self):
        filename = os.path.join(self.name, self.zip_filename)
        size_counter = self.directory_size()

        zf = ZipFile(filename, "w", zipfile.ZIP_DEFLATED)

        with tqdm(desc=self.label,
                  total=size_counter,
                  dynamic_ncols=True,
                  unit='B',
                  unit_scale=True,
                  unit_divisor=1024) as bar:

            abs_dirname = os.path.abspath(self.source_path)

            for root, dirs, files in os.walk(self.source_path):
                for f in files:
                    abs_name = os.path.abspath(os.path.join(root, f))
                    arc_name = abs_name[len(abs_dirname) + 1:]
                    zf.write(abs_name, arc_name)
                    bar.set_postfix(file=f[-10:], refresh=False)
                    bar.update(os.stat(abs_name).st_size)
        zf.close()
        return filename

    def directory_size(self):
        size_counter = 0
        for filepath in walk(self.source_path):
            size_counter += os.stat(filepath).st_size
        return size_counter


class Extractor:

    def __init__(self, *args, label="Extracting"):
        self.workspace_out_dir = build_dir(*args)
        self.label = label

    def __call__(self, data_bytes):
        zf = ZipFile(io.BytesIO(data_bytes))

        uncompress_size = sum((file.file_size for file in zf.infolist()))
        with tqdm(desc=self.label,
                  total=uncompress_size,
                  unit='B',
                  unit_scale=True,
                  unit_divisor=1024) as bar:
            for f in zf.infolist():
                filename = f.filename
                zf.extract(f, self.workspace_out_dir)
                bar.set_postfix(file=filename[-10:], refresh=False)
                bar.update(f.file_size)
