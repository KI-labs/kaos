import json
import re


def build_resource_meta(workspace,
                        user,
                        commit_id=None,
                        path=None):
    res = {'user': user, 'workspace': workspace}
    if commit_id:
        res['commit_id'] = commit_id
    if path:
        res['path'] = path

    return json.dumps(res)


def build_serve_regex(workspace):
    return re.compile(f'serve-{workspace}-.*')
