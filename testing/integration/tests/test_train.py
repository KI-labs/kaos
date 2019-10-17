import checksumdir
import glob
import os
import requests
import subprocess
import time
import uuid

from utils import hash_file, get_rand_str, parse_train_info, parse_train_list,\
    run_cmd, parse_serve_list, serve_and_assert

from PyPDF2 import PdfFileReader


TIMEOUT = 150


def train_and_assert(workspace_name, expected_pretrained_jobs):
    code, stdout, stderr = run_cmd(f"kaos train deploy -s templates/property-val/model-train/ "
                                   f"-d templates/property-val/data/")
    print(stdout.read())

    print("###############################################################")
    print("# wait until the submitted job appears in BUILDING list")
    print("###############################################################")

    building_table = []
    training_table = []
    i = 0
    while len(building_table) == 0 and i < TIMEOUT:
        code, stdout, stderr = run_cmd(f"kaos train list")
        data = stdout.read().decode('utf-8')
        building_table, training_table = parse_train_list(data)
        time.sleep(10)
        print(f"building -> {building_table}")
        print(f"training -> {training_table}")
        i += 1

    if i == TIMEOUT:
        raise Exception("timeout")

    print("###############################################################")
    print("# check that the status is JOB_RUNNING")
    print("###############################################################")

    print(building_table)
    print(training_table)
    assert len(building_table) == 1
    assert len(training_table) == expected_pretrained_jobs
    assert building_table[0][3] == 'JOB_RUNNING'

    print("###############################################################")
    print("# wait until the submitted job appears in TRAINING list")
    print("###############################################################")

    building_table = []
    training_table = []
    i = 0
    while len(training_table) <= expected_pretrained_jobs and i < TIMEOUT:
        code, stdout, stderr = run_cmd(f"kaos train list")
        data = stdout.read().decode('utf-8')
        building_table, training_table = parse_train_list(data)
        print(f"building -> {building_table}")
        print(f"training -> {training_table}")
        time.sleep(10)
        i += 1

    if i == TIMEOUT:
        raise Exception("timeout")

    print("###############################################################")
    print("# check that the job is either running or has succeeded")
    print("###############################################################")

    print(building_table)
    print(training_table)
    assert len(building_table) == 0
    assert len(training_table) == 1 + expected_pretrained_jobs
    assert training_table[0][5] in ('JOB_RUNNING', 'JOB_SUCCESS')

    print("###############################################################")
    print("# wait if any training job is still running or merging")
    print("###############################################################")

    i = 0
    while any(map(lambda row: row[5] in ('JOB_RUNNING', 'JOB_MERGING'), training_table)) and i < TIMEOUT:
        code, stdout, stderr = run_cmd(f"kaos train list")
        data = stdout.read().decode('utf-8')
        building_table, training_table = parse_train_list(data)
        print(f"building -> {building_table}")
        print(f"training -> {training_table}")
        time.sleep(10)
        i += 1

    if i == TIMEOUT:
        raise Exception("timeout")

    print("###############################################################")
    print("# check that job finished with JOB_SUCCESS status")
    print("###############################################################")

    print(building_table)
    print(training_table)
    assert len(building_table) == 0
    assert len(training_table) == 1 + expected_pretrained_jobs
    assert training_table[0][5] == 'JOB_SUCCESS'

    print("###############################################################")
    print("# check all the training artifacts")
    print("###############################################################")

    artifacts_dir = f"artifacts-{workspace_name}-{expected_pretrained_jobs}"
    os.mkdir(artifacts_dir)
    job_id = training_table[0][3]
    train_get_cmd = f"kaos train get -cdm --job_id {job_id} -o {artifacts_dir}"
    print(train_get_cmd)
    code, stdout, stderr = run_cmd(train_get_cmd)
    print(stdout.read())
    model_path_matches = glob.glob(f"{artifacts_dir}/*/*/models/*/model/model.pkl", recursive=True)
    assert len(model_path_matches) == 1

    model_path = model_path_matches[0]
    model_checksum = hash_file(model_path)
    assert os.path.getsize(model_path) // 100000 == 4

    data_path_matches = glob.glob(f"{artifacts_dir}/*/*/data", recursive=True)
    assert len(data_path_matches) == 1

    data_path = data_path_matches[0]
    assert checksumdir.dirhash(data_path) == checksumdir.dirhash("templates/property-val/data/")

    code_path_matches = glob.glob(f"{artifacts_dir}/*/*/code/property-val:*", recursive=True)
    assert len(code_path_matches) == 1

    code_path = code_path_matches[0]
    print(f"code_path -> {code_path}")
    print(f"job id -> {job_id}")
    print(f"{training_table}")
    
    assert checksumdir.dirhash(code_path, excluded_files=["__init__.py"]) == \
           checksumdir.dirhash("templates/property-val/model-train/property-val", excluded_files=["__init__.py"])

    code, stdout, stderr = run_cmd(f"kaos train info -i 0")
    data = stdout.read().decode('utf-8')
    train_info = parse_train_info(data)
    assert len(train_info) > 1

    model_id = train_info[0][3]

    print("###############################################################")
    print("# check provenance")
    print("###############################################################")

    _, stdout, _ = run_cmd(f"kaos train provenance -m {model_id} -o {artifacts_dir}")
    print(stdout.read())
    prov_path = f"{artifacts_dir}/{workspace_name.lower()}/provenance/model-{model_id}.pdf"
    assert os.path.exists(prov_path)
    assert os.path.isfile(prov_path)

    with open(prov_path, "rb") as prov_file:
        prov = PdfFileReader(prov_file, strict=False)
        print(prov.documentInfo)

    return job_id, model_id, model_checksum


def test_train(params):
    subprocess.Popen(["kaos workspace list"],
                     shell=True, stdout=subprocess.PIPE).stdout.read()

    workspace_name = get_rand_str()
    code, stdout, stderr = run_cmd(f"kaos workspace create -n {workspace_name}")
    print(stdout.read())

    code, stdout, stderr = run_cmd(f"kaos template get -n property-val")
    print(stdout.read())

    print("###############################################################")
    print("# train model and assert results")
    print("###############################################################")

    old_job_id, old_model_id, old_model_checksum = train_and_assert(workspace_name, 0)

    print("###############################################################")
    print("# deploy inference with the trained model")
    print("###############################################################")

    code, stdout, stderr = run_cmd(f"kaos train info -i 0")
    data = stdout.read().decode('utf-8')
    model_id = parse_train_info(data)[0][3]

    code, stdout, stderr = run_cmd(f"kaos serve deploy -m {model_id} -s templates/property-val/model-serve")
    print(stdout.read())

    serve_and_assert(deploy_command=f"kaos serve deploy -m {model_id} -s templates/property-val/model-serve",
                     list_command="kaos serve list")

    code, stdout, stderr = run_cmd("kaos serve list")
    data = stdout.read().decode('utf-8')
    building_table, serving_table = parse_serve_list(data)

    print("###############################################################")
    print("# curl the running model")
    print("###############################################################")

    data = open("templates/property-val/test_payload.json").read()

    endpoint_name = serving_table[0][2]
    print(f"endpoing name: {endpoint_name}")
    r = requests.post(f"http://localhost:{params['k8s_port']}/{endpoint_name}/invocations",
                      headers={"Content-Type": "application/json"},
                      data=data)

    assert r.status_code == 200
    assert "result" in r.json()

    print("###############################################################")
    print("# check all the serving artifacts")
    print("###############################################################")

    serve_artifacts_dir = f"serve_artifacts-{workspace_name}"
    os.mkdir(serve_artifacts_dir)
    code, stdout, stderr = run_cmd(f"kaos serve get -e {endpoint_name} -o {serve_artifacts_dir}")
    print(stdout.read())

    serve_code_path_matches = glob.glob(f"{serve_artifacts_dir}/*/*/code/property-val:*", recursive=True)
    assert len(serve_code_path_matches) == 1
    serve_code_path = serve_code_path_matches[0]
    assert checksumdir.dirhash(serve_code_path, excluded_files=["__init__.py", "model.pkl"]) ==\
           checksumdir.dirhash("templates/property-val/model-serve/property-val",
                               excluded_files=["__init__.py", "model.pkl"])

    model_path_matches = glob.glob(f"{serve_artifacts_dir}/*/*/code/property-val:*/model/model.pkl", recursive=True)
    assert len(model_path_matches) == 1

    model_path = model_path_matches[0]
    assert os.path.getsize(model_path) // 100000 == 4

    _, stdout, _ = run_cmd(f"kaos serve provenance -e {endpoint_name} -o {serve_artifacts_dir}")
    print(stdout.read())

    serve_provenance_matches = glob.glob(f"{serve_artifacts_dir}/{workspace_name.lower()}/provenance/serve-*.pdf",
                                         recursive=True)
    assert len(serve_provenance_matches) == 1

    serve_provenance_path = serve_provenance_matches[0]
    assert os.path.exists(serve_provenance_path)
    assert os.path.isfile(serve_provenance_path)

    with open(serve_provenance_path, "rb") as prov_file:
        prov = PdfFileReader(prov_file, strict=False)
        print(prov.documentInfo)

    print("###############################################################")
    print("# modify code dir")
    print("###############################################################")

    with open(f"templates/property-val/model-train/property-val/model/{uuid.uuid4().hex}", 'w') as f:
        f.write(uuid.uuid4().hex)

    print("###############################################################")
    print("# RE-train model and assert results")
    print("###############################################################")

    train_and_assert(workspace_name, 1)

    # ###############################################################
    # # modify data dir
    # ###############################################################
    #
    # with open(f"templates/property-val/data/features{uuid.uuid4().hex}", 'w') as f:
    #     f.write(uuid.uuid4().hex)
    #
    # ###############################################################
    # # RE-train model and assert results
    # ###############################################################
    #
    # train_and_assert(workspace_name, 2)

    print("# ##############################################################")
    print("# Check that we can still get the actual old model")
    print("# ##############################################################")

    old_artifacts_dir = f"old-artifacts-{workspace_name}"
    os.mkdir(old_artifacts_dir)
    code, stdout, stderr = run_cmd(f"kaos train get -cdm --job_id {old_job_id} -o {old_artifacts_dir}")
    print(stdout.read())
    old_model_path_matches = glob.glob(f"{old_artifacts_dir}/*/*/models/*/model/model.pkl", recursive=True)
    assert len(old_model_path_matches) == 1

    old_model_path = old_model_path_matches[0]
    old_model_checksum_now = hash_file(old_model_path)
    assert old_model_checksum == old_model_checksum_now
