import boto3

from kaos_backend.constants import DOCKER_REGISTRY, REGION, CLOUD_PROVIDER


def get_login_command():
    if CLOUD_PROVIDER == 'AWS':
        # ecr = boto3.client('ecr', region_name=REGION)
        #
        # raw_auth_data = ecr.get_authorization_token()['authorizationData'][0]['authorizationToken']
        # _, docker_auth_token = b64decode(raw_auth_data).decode('UTF-8').split(":")
        return f"$(aws ecr get-login --region {REGION} --no-include-email)"
    elif CLOUD_PROVIDER == "GCP":
        return f"gcloud auth print-access-token | docker login -u oauth2accesstoken --password-stdin https://{DOCKER_REGISTRY}"
    else:
        return ""


def create_docker_repo(repo_name):
    if CLOUD_PROVIDER == 'AWS':
        ecr = boto3.client('ecr', region_name=REGION)
        ecr.create_repository(repositoryName=repo_name)


def delete_docker_repo(repo_name):
    if CLOUD_PROVIDER == 'AWS':
        ecr = boto3.client('ecr', region_name=REGION)
        ecr.delete_repository(repositoryName=repo_name, force=True)
