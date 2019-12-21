import checksumdir
import glob
import os
import requests
import time
import json

from utils import hash_file, get_rand_str, parse_train_info, parse_train_list, \
    run_cmd, run_cmd_error_check, parse_serve_list, serve_and_assert, pretty_print

from PyPDF2 import PdfFileReader

TIMEOUT_S = 600


class TrainJob:

    @staticmethod
    def parse_data(data):
        return parse_train_list(data)

    @staticmethod
    def get_state_col():
        return 5

    @staticmethod
    def get_acceptable_job_states():
        return 'JOB_RUNNING', 'JOB_MERGING', 'JOB_SUCCESS'

    @staticmethod
    def get_job_completion_states():
        return 'JOB_SUCCESS'

    @staticmethod
    def get_list_jobs_cmd():
        return "kaos train list"


class ServeJob:

    @staticmethod
    def parse_data(data):
        return parse_serve_list(data)

    @staticmethod
    def get_state_col():
        return 3

    @staticmethod
    def get_acceptable_job_states():
        return 'PIPELINE_STARTING', 'PIPELINE_RUNNING', 'PIPELINE_RESTARTING', 'PIPELINE_STANDBY'

    @staticmethod
    def get_job_completion_states():
        return 'PIPELINE_RUNNING'

    @staticmethod
    def get_list_jobs_cmd():
        return "kaos serve list"


def deployment_assert(already_present_jobs,
                      job,
                      env=None):
    """Check the training/serving job stages and wait until they complete.
    """
    pretty_print("BEGIN deployment assert")

    st_col = job.get_state_col()  # the table column with the job status
    acceptable_job_states = job.get_acceptable_job_states()
    job_completion_states = job.get_job_completion_states()
    list_jobs_cmd = job.get_list_jobs_cmd()

    deployment_stage_done = False
    deployment_stage_done_visible_jobs = False

    start = time.time()
    building_table_prev, deployment_table_prev = None, None

    while not all([deployment_stage_done,
                   deployment_stage_done_visible_jobs]):

        # not necessary in the ideal case
        time.sleep(2)

        # list jobs
        code, stdout, stderr = run_cmd(list_jobs_cmd, env=env)
        run_cmd_error_check(code, stderr)

        data = stdout.read().decode('utf-8')
        building_table, deployment_table = job.parse_data(data)

        if (building_table_prev != building_table) or deployment_table_prev != deployment_table:
            pretty_print('Change in state')
            building_table_prev = building_table
            deployment_table_prev = deployment_table
            print(stdout.read().decode("utf-8"))
            print(f"building -> {building_table}")
            print(f"deployment -> {deployment_table}")

        # sometimes the image is build so fast that you are not able to catch this stage
        if len(building_table) > 0:
            assert len(building_table) == 1
            assert len(deployment_table) == already_present_jobs
            assert building_table[0][-1] == 'JOB_RUNNING'

        if len(deployment_table) > already_present_jobs:
            assert len(building_table) == 0
            assert len(deployment_table) == already_present_jobs + 1
            assert deployment_table[0][st_col] in acceptable_job_states

            deployment_stage_done = deployment_table[0][st_col] in job_completion_states

        deployment_stage_done_visible_jobs = all(map(lambda row: row[st_col] in job_completion_states, deployment_table))

        # print('exec_stage_done, exec_stage_done_visible_jobs: ', exec_stage_done, exec_stage_done_visible_jobs)

        if (time.time() - start) > TIMEOUT_S:
            raise Exception("timeout")

    pretty_print("END deployment assert")


def train_artifacts_assert(workspace_name, template_name, job_id, already_present_training_jobs, hyperparam_comb=0,
                           env=None):
    pretty_print("check all the training artifacts")

    artifacts_dir = f"artifacts-{workspace_name}-{already_present_training_jobs}"
    os.mkdir(artifacts_dir)

    train_get_cmd = f"kaos train get -cdm --job_id {job_id} -o {artifacts_dir}"
    print(train_get_cmd)

    code, stdout, stderr = run_cmd(train_get_cmd, env=env)
    run_cmd_error_check(code, stderr)
    print(stdout.read().decode("utf-8"))

    model_path_matches = glob.glob(f"{artifacts_dir}/*/*/models/*/model/model.pkl", recursive=True)
    assert len(model_path_matches) == max(1, hyperparam_comb)

    model_path = model_path_matches[0]
    model_checksum = hash_file(model_path)

    data_path_matches = glob.glob(f"{artifacts_dir}/*/*/data", recursive=True)
    assert len(data_path_matches) == 1

    data_path = data_path_matches[0]
    assert checksumdir.dirhash(data_path) == checksumdir.dirhash(f"templates/{template_name}/data/")

    code_path_matches = glob.glob(f"{artifacts_dir}/*/*/code/{template_name}:*", recursive=True)
    assert len(code_path_matches) == 1

    code_path = code_path_matches[0]
    assert checksumdir.dirhash(code_path, excluded_files=["__init__.py"]) == \
           checksumdir.dirhash(f"templates/{template_name}/model-train/{template_name}", excluded_files=["__init__.py"])

    code_path = code_path_matches[0]

    print(f"code_path -> {code_path}")
    print(f"job id -> {job_id}")

    return artifacts_dir, model_checksum


def train_info_assert(metrics_sort=(), env=None):
    # check train info
    pretty_print("check `train info`")

    code, stdout, stderr = run_cmd(f"kaos train info -i 0", env=env)
    run_cmd_error_check(code, stderr)

    data = stdout.read().decode('utf-8')
    train_info = parse_train_info(data)
    print(data)
    assert len(train_info) > 1

    # check train info -s
    for metric in metrics_sort:
        pretty_print(f"check `train info -s {metric}`")

        code, stdout, stderr = run_cmd(f"kaos train info -i 0 -s {metric}", env=env)
        run_cmd_error_check(code, stderr)

        data = stdout.read().decode('utf-8')
        print(data)

    return train_info


def train_provenance_assert(workspace_name, model_id, artifacts_dir, env=None):
    pretty_print("check provenance")

    code, stdout, stderr = run_cmd(f"kaos train provenance -m {model_id} -o {artifacts_dir}", env=env)
    run_cmd_error_check(code, stderr)

    print(stdout.read().decode('utf-8'))
    prov_path = f"{artifacts_dir}/{workspace_name.lower()}/provenance/model-{model_id}.pdf"

    assert os.path.exists(prov_path)
    assert os.path.isfile(prov_path)

    with open(prov_path, "rb") as prov_file:
        prov = PdfFileReader(prov_file, strict=False)
        print(prov.documentInfo)


def curl_mnist_model(port, endpoint_name, env=None):
    pretty_print("curl served mnist model")
    code, stdout, stderr = run_cmd(
        f"curl -X POST http://localhost:{port}/{endpoint_name}/invocations --data-binary @templates/mnist/test_payload.jpg",
        env=env)
    run_cmd_error_check(code, stderr)

    data = stdout.read().decode('utf-8')
    assert json.loads(data) == {'result': [3]}

    print(data)


def train(template_name, already_present_training_jobs, env=None):
    pretty_print("BEGIN `train` job \n# Submit source code and training data ")
    code, stdout, stderr = run_cmd(f"kaos train deploy "
                                   f"-s templates/{template_name}/model-train/ "
                                   f"-d templates/{template_name}/data/", env=env)

    run_cmd_error_check(code, stderr)
    print(stdout.read().decode("utf-8"))

    # check training job stages and wait until training is completed
    deployment_assert(already_present_training_jobs, job=TrainJob, env=env)

    pretty_print("END `train` job")


def train_hyper(template_name, already_present_training_jobs, env=None):
    # submit source code
    pretty_print("BEGIN `train hyper` job \n# submit source code")

    code, stdout, stderr = run_cmd(f"kaos train deploy "
                                   f"-s templates/{template_name}/model-train/ ", env=env)

    run_cmd_error_check(code, stderr)
    print(stdout.read().decode("utf-8"))

    time.sleep(5)

    # submit hyperparameters
    pretty_print('submit hyperparameters')
    code, stdout, stderr = run_cmd(f"kaos train deploy "
                                   f"-h templates/{template_name}/hyperopt/params.json "
                                   f"-d templates/{template_name}/data/", env=env)

    run_cmd_error_check(code, stderr)
    print(stdout.read().decode("utf-8"))

    # check training job stages and wait until training is completed
    deployment_assert(already_present_training_jobs, job=TrainJob, env=env)

    pretty_print("END `train hyper` job")


def post_train_assert(workspace_name, template_name, already_present_training_jobs,
                      metrics_sort=(),
                      hyperparam_comb=0,
                      env=None):
    """ Check commands that are used to inspect the results of a training job.
    """

    pretty_print("BEGIN assert `train` job")

    code, stdout, stderr = run_cmd(f"kaos train list", env=env)
    run_cmd_error_check(code, stderr)

    data = stdout.read().decode('utf-8')
    print(data)
    building_table, training_table = parse_train_list(data)
    job_id = training_table[0][3]

    # check all the training artifacts
    artifacts_dir, model_checksum = train_artifacts_assert(workspace_name, template_name, job_id,
                                                           already_present_training_jobs, hyperparam_comb, env=env)

    # check train info
    train_info = train_info_assert(metrics_sort, env=env)

    # check provenance
    model_id = train_info[0][3]
    train_provenance_assert(workspace_name, model_id, artifacts_dir, env=env)

    pretty_print("END assert `train` job")

    return job_id, model_id, model_checksum


def serve(template_name, already_present_serving_jobs, model_id, env=None):
    pretty_print(' BEGIN `serve` job')

    pretty_print('Submit a `serve` job: source code and serving model')
    code, stdout, stderr = run_cmd(f"kaos serve deploy "
                                   f"-m {model_id} "
                                   f"-s templates/{template_name}/model-serve", env=env)

    run_cmd_error_check(code, stderr)
    print(stdout.read().decode("utf-8"))

    # check serving job stages and wait until the serving stage is complleted
    deployment_assert(already_present_serving_jobs, job=ServeJob, env=env)

    pretty_print(' END `serve` job')


def post_serve_assert(workspace_name: str, template_name='property-val', port=80, env=None):
    pretty_print("BEGIN assert `serve` job")

    # ugly hack
    time.sleep(10)

    code, stdout, stderr = run_cmd(f"kaos serve list", env=env)
    run_cmd_error_check(code, stderr)

    data = stdout.read().decode('utf-8')
    building_table, serving_table = parse_serve_list(data)
    print(data)
    print(f"building -> {building_table}")
    print(f"exec -> {serving_table}")

    endpoint_name = serving_table[0][2]
    print(f"endpoing name: {endpoint_name}")

    # get serve artifacts
    pretty_print("get serve artifacts")

    serve_artifacts_dir = f"serve_artifacts-{workspace_name}"
    os.mkdir(serve_artifacts_dir)
    print(f"serve_artifacts_dir: {serve_artifacts_dir}")

    code, stdout, stderr = run_cmd(f"kaos serve get -e {endpoint_name} -o {serve_artifacts_dir}", env=env)
    run_cmd_error_check(code, stderr)

    # check artifacts
    pretty_print("check artifacts")

    serve_code_path_matches = glob.glob(f"{serve_artifacts_dir}/*/*/code/{template_name}:*", recursive=True)
    assert len(serve_code_path_matches) == 1
    serve_code_path = serve_code_path_matches[0]
    assert checksumdir.dirhash(serve_code_path, excluded_files=["__init__.py", "model.pkl"]) == \
           checksumdir.dirhash(f"templates/{template_name}/model-serve/{template_name}",
                               excluded_files=["__init__.py", "model.pkl"])

    model_path_matches = glob.glob(f"{serve_artifacts_dir}/*/*/code/{template_name}:*/model/model.pkl", recursive=True)
    assert len(model_path_matches) == 1

    # provenance
    pretty_print("check provenance")

    code, stdout, stderr = run_cmd(f"kaos serve provenance -e {endpoint_name} -o {serve_artifacts_dir}", env=env)
    run_cmd_error_check(code, stderr)

    print(stdout.read().decode('utf-8'))
    provenance_matches = glob.glob(f"{serve_artifacts_dir}/{workspace_name.lower()}/provenance/serve-*.pdf",
                                   recursive=True)
    print('provenance_matches: ', provenance_matches)

    assert len(provenance_matches) == 1

    serve_provenance_path = provenance_matches[0]
    assert os.path.exists(serve_provenance_path)
    assert os.path.isfile(serve_provenance_path)

    with open(serve_provenance_path, "rb") as prov_file:
        prov = PdfFileReader(prov_file, strict=False)
        print(prov.documentInfo)

    if template_name == 'mnist':
        # send a request to the endpoint
        curl_mnist_model(port, endpoint_name)
    elif template_name == 'property-val':

        data = open(f"templates/{template_name}/test_payload.json").read()
        print('data \n', data)

        endpoint_name = serving_table[0][2]
        print(f"endpoing name: {endpoint_name}")
        r = requests.post(f"http://localhost:{port}/{endpoint_name}/invocations",
                          headers={"Content-Type": "application/json"},
                          data=data)

        assert r.status_code == 200
        assert "result" in r.json()

    pretty_print("END assert `serve` job")


def test(params, template_name='property-val', env=None):
    print('testing...')

    port = params['k8s_port']

    # check workspace
    code, stdout, stderr = run_cmd("kaos workspace list", env=env)
    run_cmd_error_check(code, stderr)
    print(stdout.read().decode("utf-8"))

    # create workspace
    workspace_name = get_rand_str()
    code, stdout, stderr = run_cmd(f"kaos workspace create -n {workspace_name}", env=env)
    run_cmd_error_check(code, stderr)
    print(stdout.read().decode("utf-8"))

    # get template
    code, stdout, stderr = run_cmd(f"kaos template get -n {template_name}", env=env)
    run_cmd_error_check(code, stderr)
    print(stdout.read().decode("utf-8"))

    # train (single job)
    train(template_name=template_name,
          already_present_training_jobs=0,
          env=env)

    # cheparamsck job artifacts
    job_id, model_id, model_checksum = post_train_assert(workspace_name,
                                                         template_name,
                                                         already_present_training_jobs=1,
                                                         env=env)

    # train using a hyperparam grid (single job)
    train_hyper(template_name,
                already_present_training_jobs=1,
                env=env)

    job_id, model_id, model_checksum = post_train_assert(workspace_name,
                                                         template_name,
                                                         already_present_training_jobs=2,
                                                         hyperparam_comb=8,
                                                         metrics_sort=('MAE_test', 'R2_test'),
                                                         env=env)

    serve(template_name=template_name,
          already_present_serving_jobs=0,
          model_id=model_id,
          env=env)

    post_serve_assert(workspace_name,
                      template_name,
                      port,
                      env=env)
