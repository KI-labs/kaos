import time

import requests
from configobj import ConfigObj
from kaos_cli.constants import CONFIG_PATH
from utils import run_cmd, parse_serve_list, serve_and_assert, get_rand_str

TIMEOUT = 150


def test_notebook(params):
    workspace_name = get_rand_str()
    code, stdout, stderr = run_cmd(f"kaos workspace create -n {workspace_name}")
    print(stdout.read())

    code, stdout, stderr = run_cmd(f"kaos template get -n notebook")
    print(stdout.read())

    serve_and_assert(deploy_command="kaos notebook deploy -s templates/notebook",
                     list_command="kaos notebook list")

    code, stdout, stderr = run_cmd("kaos notebook list")
    data = stdout.read().decode('utf-8')
    building_table, serving_table = parse_serve_list(data)

    print("###############################################################")
    print("# curl the running notebook")
    print("###############################################################")

    i = 0
    cond = True
    r = {}

    # Get the token for authorizing with the serve endpoint
    config = ConfigObj(CONFIG_PATH)
    try:
        token = config["MINIKUBE"]["backend"]["token"]
    except KeyError:
        token = config["DOCKER"]["backend"]["token"]

    while i < TIMEOUT and cond:
        r = requests.get(f"http://localhost:{params['k8s_port']}/{serving_table[0][2]}/lab", allow_redirects=True,
                         headers={"X-Authorization-Token": token})
        cond = r.status_code > 200
        time.sleep(10)
        i += 10

    assert r.status_code == 200

    run_cmd("yes y | kaos workspace kill")
