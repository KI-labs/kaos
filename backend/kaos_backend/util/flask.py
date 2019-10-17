import functools
from flask import jsonify as flask_jsonify

from kaos_model.api import Response, PagedResponse, Error


# jsonify response decorator
def jsonify(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        obj = f(*args, **kwargs)
        if type(obj) in (Response, PagedResponse, Error):
            obj = obj.to_dict()
        return flask_jsonify(obj)
    return wrapped
