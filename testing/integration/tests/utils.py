import hashlib
import random
import string
import subprocess
import time

TIMEOUT = 150


def hash_file(path):
    hasher = hashlib.sha3_256()
    with open(path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()


def get_rand_str():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))


def find(lst, item, start_idx=0):
    try:
        return lst.index(item, start_idx)
    except ValueError:
        return -1


def tokenize(raw_output):
    data_lines = [l for l in raw_output.splitlines(keepends=False) if l.count('+') == 0]
    tokens = [[raw_token.strip() for raw_token in line.split("|") if raw_token] for line in data_lines]
    return tokens


def extract_table(token_lines, header, header_offset=1):
    start_idx = max(find(token_lines, header), 0)
    end_idx = find(token_lines, [], start_idx)
    end_idx = None if end_idx < 0 else end_idx

    if start_idx >= 0:
        return token_lines[start_idx + header_offset:end_idx]
    else:
        return None


# WARNING: DOES NOT GROUP MULTILINE CELLS
def parse_train_list(data):
    tokens = tokenize(data)

    building_table = extract_table(tokens, ["BUILDING"], header_offset=2)
    training_table = extract_table(tokens, ["TRAINING"], header_offset=2)
    return building_table, training_table


def parse_train_info(data):
    tokens = tokenize(data)
    print(tokens)

    return extract_table(tokens, ['ind', 'Code', 'Data', 'Model ID', 'Hyperparams'])


def parse_serve_list(data):
    tokens = tokenize(data)

    building_table = extract_table(tokens, ["BUILDING"], header_offset=2)
    serving_table = extract_table(tokens, ["RUNNING"], header_offset=2)
    return building_table, serving_table


def run_cmd(cmd, env=None):
    print(cmd)
    prc = subprocess.Popen([cmd],
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           env=env)
    prc.wait()
    return prc.returncode, prc.stdout, prc.stderr


def run_cmd_error_check(code, stderr):
    if code > 0:
        if stderr is not None:
            stderr = stderr.read().decode('utf-8')
        raise Exception(f"run cmd error:\n{stderr}")


def pretty_print(txt):
    print("\n###############################################################\n"
          f"# {txt}"
          "\n###############################################################\n")


def serve_and_assert(deploy_command, list_command):
    code, stdout, stderr = run_cmd(deploy_command)
    print(stdout.read())

    building_table = []
    serving_table = []
    i = 0
    while len(building_table) == 0 and i < TIMEOUT:
        code, stdout, stderr = run_cmd(list_command)
        data = stdout.read().decode('utf-8')
        building_table, serving_table = parse_serve_list(data)
        time.sleep(10)
        print(f"building -> {building_table}")
        print(f"serving -> {serving_table}")
        i += 1

    if i == TIMEOUT:
        raise Exception("timeout")

    assert len(building_table) == 1
    assert len(serving_table) == 0
    assert building_table[0][-1] == 'JOB_RUNNING'

    building_table = []
    serving_table = []
    i = 0
    while len(serving_table) == 0 and i < TIMEOUT:
        code, stdout, stderr = run_cmd(list_command)
        data = stdout.read().decode('utf-8')
        building_table, serving_table = parse_serve_list(data)
        time.sleep(10)
        print(f"building -> {building_table}")
        print(f"serving -> {serving_table}")
        i += 1

    if i == TIMEOUT:
        raise Exception("timeout")

    assert serving_table[0][3] in ('PIPELINE_RUNNING', 'PIPELINE_STARTING', 'PIPELINE_RESTARTING', 'PIPELINE_STANDBY')

    waiting_states = ('PIPELINE_STARTING', 'PIPELINE_RESTARTING', 'PIPELINE_STANDBY')
    i = 0
    while serving_table[0][3] in waiting_states and i < TIMEOUT:
        code, stdout, stderr = run_cmd(list_command)
        data = stdout.read().decode('utf-8')
        building_table, serving_table = parse_serve_list(data)
        print(f"building -> {building_table}")
        print(f"serving -> {serving_table}")
        time.sleep(10)
        i += 1

    if i == TIMEOUT:
        raise Exception("timeout")

    print(building_table)
    print(serving_table)
    assert len(building_table) == 0
    assert len(serving_table) == 1
    assert serving_table[0][3] == 'PIPELINE_RUNNING'
