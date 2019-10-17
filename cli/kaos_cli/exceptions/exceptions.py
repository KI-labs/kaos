class SimpleApplicationError(Exception):
    def __init__(self, message=None):
        self.message = message


class MissingArgumentError(SimpleApplicationError):
    pass


class HostnameError(SimpleApplicationError):
    pass


class RequestError(SimpleApplicationError):
    pass


class VersionError(SimpleApplicationError):
    pass


class InvalidWorkspaceError(SimpleApplicationError):
    pass


class NoTrainingJobsError(SimpleApplicationError):
    pass


class NoServingJobsError(SimpleApplicationError):
    pass


class NoNotebookError(SimpleApplicationError):
    pass


class CommandError(Exception):
    def __init__(self, missing_commands):
        self.commands = missing_commands


class WorkspaceExistsError(Exception):
    def __init__(self, name):
        self.name = name
