import json
import logging
import re

from grpc._channel import _Rendezvous
from flask import current_app

from kaos_backend.exceptions.exceptions import UnfinishedCommitError, CommitNotFoundError, PachydermError

DESCRIPTION = 'description'
GRPC_MESSAGE = 'grpc_message'

UNFINISHED_COMMIT_RE = re.compile("output commit (.+) not finished")
COMMIT_NOT_FOUND_RE = re.compile("commit (.+) not found in repo")
COULD_NOT_CONNECT_RE = re.compile("Failed to pick subchannel")


def recover(f, err_types, recover_f):
    try:
        return f()
    except Exception as e:
        if type(e) in err_types:
            logging.warning(str(e))
            return recover_f()
        else:
            raise e


def handle_pachyderm_error(f):
    def wrapper(*args, **kwargs):
        try:
            a = f(*args, **kwargs)
            return a
        except _Rendezvous as e:
            print(e.debug_error_string())
            err_desc = json.loads(e.debug_error_string())
            current_app.logger.error("@handle_pachyderm_error: %s", str(err_desc))

            grpc_message = err_desc.get(GRPC_MESSAGE, None)
            current_app.logger.error("@handle_pachyderm_error: %s", grpc_message)

            if grpc_message:
                match = UNFINISHED_COMMIT_RE.match(grpc_message)
                if match:
                    raise UnfinishedCommitError(match[0]) from e

                match = COMMIT_NOT_FOUND_RE.findall(grpc_message)
                if match:
                    raise CommitNotFoundError(match[0]) from e

            description_message = err_desc.get(DESCRIPTION, None)
            current_app.logger.error("@handle_pachyderm_error: %s", description_message)

            if description_message:
                if COULD_NOT_CONNECT_RE.match(description_message):
                    raise PachydermError(description_message) from e

            raise PachydermError(str(e)) from e

    return wrapper
