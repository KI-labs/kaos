import os
from tempfile import TemporaryDirectory, NamedTemporaryFile
from zipfile import ZipFile


def create_zip_file(dirname):
    zipfile = ZipFile("zip.zip", "w")
    abs_dirname = os.path.abspath(dirname)

    for root, dirs, files in os.walk(dirname):
        for f in files:
            abs_name = os.path.abspath(os.path.join(root, f))
            arc_name = abs_name[len(abs_dirname) + 1:]
            zipfile.write(abs_name, arc_name)
    zip_filename = zipfile.filename
    zipfile.close()
    return zip_filename


def create_zip():
    t = TemporaryDirectory()
    f = NamedTemporaryFile(dir=t.name, delete=True)
    f.file.write(b'01')
    zip_filename = create_zip_file(t.name)
    with open(zip_filename, 'rb') as file_data:
        bytes_content = file_data.read()
    f.close()
    return bytes_content, f, t, zip_filename


def create_zip_with_ds_store():
    t = TemporaryDirectory()
    f = open(os.path.join(t.name, ".DS_Store"), "w")
    f.write('01')
    f.close()
    zip_filename = create_zip_file(t.name)
    with open(zip_filename, 'rb') as file_data:
        bytes_content = file_data.read()
    return bytes_content, t, zip_filename
