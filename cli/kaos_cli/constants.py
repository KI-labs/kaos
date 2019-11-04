import os
from distutils.version import StrictVersion

import kaos_cli

KAOS_STATE_DIR = os.path.abspath("./.kaos")
KAOS_INSTALLATION_DIR = os.path.dirname(kaos_cli.__file__)

#Config spec path
CONFIG_SPEC = os.path.abspath("./config_spec")

# Project name
PROJECT = os.environ.get("PROJECT", "kaos")
CONFIG_PATH = os.path.join(KAOS_STATE_DIR, "config")

# Template path
TEMPLATE_DIR = os.path.join(KAOS_INSTALLATION_DIR, "resources", "templates")

# Minimal cache
WORKSPACE_CACHE = os.path.join(KAOS_STATE_DIR, ".workspace.cache")
NOTEBOOK_CACHE = os.path.join(KAOS_STATE_DIR, ".notebook.cache")
TRAIN_CACHE = os.path.join(KAOS_STATE_DIR, ".train.cache")
SERVE_CACHE = os.path.join(KAOS_STATE_DIR, ".serve.cache")

KAOS_HOME = os.getenv("KAOS_HOME", "")

# local TF path
DOCKER_TF_PATH = os.path.join(KAOS_HOME, 'infrastructure', 'docker')
MINIKUBE_TF_PATH = os.path.join(KAOS_HOME, 'infrastructure', 'minikube')
AWS_TF_PATH = os.path.join(KAOS_HOME, 'infrastructure', 'aws', 'envs')
GCP_TF_PATH = os.path.join(KAOS_HOME, 'infrastructure', 'gcp', 'envs')
AZURE_TF_PATH = os.path.join(KAOS_HOME, 'infrastructure', 'azure', 'envs')

GCP_LOCAL_BACKEND_PATH = os.path.join(KAOS_HOME, 'infrastructure', 'gcp', 'backend_local', 'config.tf')
AWS_LOCAL_BACKEND_PATH = os.path.join(KAOS_HOME, 'infrastructure', 'aws', 'backend_local', 'config.tf')
AZURE_LOCAL_BACKEND_PATH = os.path.join(KAOS_HOME, 'infrastructure', 'azure', 'backend_local', 'config.tf')

# kaos TF path
KAOS_TF_PATH = os.path.join(KAOS_STATE_DIR, 'state')

# Provider vars
DOCKER = "DOCKER"
MINIKUBE = "MINIKUBE"
AWS = "AWS"
AZ = "AZ"
GCP = "GCP"

# environments in config
ENVIRONMENTS = 'environments'

LOCAL_CONFIG_DICT = dict(AWS=AWS_LOCAL_BACKEND_PATH,
                         AZ=AZURE_LOCAL_BACKEND_PATH,
                         GCP=GCP_LOCAL_BACKEND_PATH)

PROVIDER_DICT = dict(DOCKER=DOCKER_TF_PATH,
                     MINIKUBE=MINIKUBE_TF_PATH,
                     AWS=AWS_TF_PATH,
                     AZ=AZURE_TF_PATH,
                     GCP=GCP_TF_PATH)

ENV_DICT = dict(DOCKER=[],
                MINIKUBE=[],
                AWS=["AWS_ACCESS_KEY_ID",
                     "AWS_SECRET_ACCESS_KEY",
                     "AWS_DEFAULT_REGION"],
                AZ=["TF_VAR_CLIENT_ID",
                    "TF_VAR_CLIENT_SECRET",
                    "TF_VAR_SERVICE_PRINCIPAL_ID",
                    "TF_VAR_SERVICE_PRINCIPAL_SECRET",
                    "TF_VAR_SUBSCRIPTION_ID",
                    "TF_VAR_TENANT_ID",
                    "TF_VAR_registry_email",
                    "ARM_ACCESS_KEY"],
                GCP=[])

# terraform dir, files and version
TF_DIR = os.path.join(".", ".terraform")
TF_STATE = "terraform.tfstate"
TF_STATE_BACKUP = "terraform.tfstate.backup"
KUBECONFIG_ENV = "KUBECONFIG"
TF_CONFIG_JSON = os.path.abspath(os.path.join(".", "config.json"))
MINIMAL_TF_VERSION = StrictVersion("0.12.7")

# unicode visualization (https://unicode-table.com/)
SYM_CHECK = "\u2714"
SYM_CROSS = "\u2717"
SYM_PROGRESS = "\u2A02"
METADATA_JSON = "metadata.json"
DEFAULTS = {
    "user": os.environ.get("USER", "kaos")
}
DEFAULT = 'default'
BACKEND = 'backend'
INFRASTRUCTURE = "infrastructure"
PACHYDERM = 'pachyderm'
CONTEXTS = 'contexts'
ACTIVE = 'active'
