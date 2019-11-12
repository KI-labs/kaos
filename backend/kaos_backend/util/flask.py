import functools
from flask import jsonify as flask_jsonify
from google.protobuf.empty_pb2 import Empty

from kaos_model.api import Response, PagedResponse, Error


# jsonify response decorator
def jsonify(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        obj = f(*args, **kwargs)
        if type(obj) in (Response, PagedResponse, Error):
            obj = obj.to_dict()
        if type(obj) is dict:
            obj = {k: None if isinstance(v, Empty) else v for k, v in obj.items()}
        return flask_jsonify(obj)

    return wrapped
