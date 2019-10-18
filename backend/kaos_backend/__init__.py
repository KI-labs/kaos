import os

_ROOT = os.path.abspath(os.path.dirname(__file__))


def get_resource(path):
    return os.path.join(_ROOT, 'resources', path)
