#!/usr/bin/env bash

set -e

infrastructure=$1
cd ${infrastructure}

function tf_validate() {
    terraform init
    terraform validate
    rm -r .terraform/
}

function validate_environments() {
    for env in "dev" "prod" "stage"
    do
        pushd "$env"
        tf_validate
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
        tf_validate
        popd
        break
    fi

    validate_environments

	popd
done
