from google.protobuf.json_format import MessageToDict


def proto_to_dict(f):
    """
    Creates dict from protobuf return value
    """
    def wrapped(*args, **kwargs):
        resp = f(*args, **kwargs)
        if resp is not None:
            return MessageToDict(resp)
        else:
            return None
    return wrapped
