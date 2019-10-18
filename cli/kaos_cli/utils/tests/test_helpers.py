import os
from tempfile import TemporaryDirectory, NamedTemporaryFile

from kaos_cli.utils.helpers import Compressor, build_dir


def create_tmp():
    t = TemporaryDirectory()
    f = NamedTemporaryFile(dir=t.name, delete=True)
    f.file.write(b'01')
    return t


def test_single_ds_store_bundle():
    t = create_tmp()

    with Compressor(label="test", filename="model.zip", source_path=t.name) as tmp:
        assert os.path.exists(tmp) is True

    t.cleanup()


def test_build_dir():
    t = TemporaryDirectory()
    path = build_dir(t.name, "something", "something")
    assert os.path.exists(path)
    t.cleanup()
