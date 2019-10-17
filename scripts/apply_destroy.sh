#!/usr/bin/env bash

set -e

infrastructure=$1
cd ${infrastructure}

function tf_apply_destroy() {
    if [[ ! -f done ]]; then
        terraform init

        if [[ $# -eq 1 ]]; then
            terraform workspace select "$1"
        fi

        terraform apply --auto-approve
        terraform destroy --auto-approve
        rm -r .terraform/
        touch done
    fi
}

function apply_destroy_environments() {
    for env in "dev" "prod" "stage"
    do
        pushd "$env"
        tf_apply_destroy "$env"
        popd
    done
}

for cloud in "aws" "azure" "gcp" "local"
do
    env_dir="$cloud/envs"

    if [[ -d "$env_dir" ]]; then
        pushd "$env_dir"
    else
        pushd "$cloud"
        tf_apply_destroy
        popd
        break
    fi

    apply_destroy_environments

	popd
done
