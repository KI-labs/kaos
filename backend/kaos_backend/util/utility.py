import os


def flatten(l):
    return [item for sublist in l for item in sublist]


def get_dir_and_files(tmp):
    return flatten([dir + files for _, dir, files in os.walk(tmp)])


def repeated_call(n):
    def decorator(function):
        def wrapper(*args, **kwargs):
            for i in range(n):
                function(*args, **kwargs)
        return wrapper
    return decorator
