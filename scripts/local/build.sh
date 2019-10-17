#!/bin/bash
set -e

function check_deps() {
  test -f $(which docker) || error_exit "docker command not detected in path, please install it"
}

# define arguments
for i in "$@"
do
case ${i} in
    -i=*|--image=*)
    IMAGE="${i#*=}"
    shift # past argument=value
    ;;
    -t=*|--tag=*)
    TAG="${i#*=}"
    shift # past argument=value
    ;;
    -c=*|--context=*)
    DOCKER_CONTEXT="${i#*=}"
    shift # past argument=value
    ;;
    -f=*|--dockerfile=*)
    DOCKERFILE="${i#*=}"
    shift # past argument=value
    ;;
    -m=*|--minikube=*)
    eval $(minikube docker-env)
    shift # past argument=value
    ;;
    *)
          # unknown option
    ;;
esac
done

# assign default values (if needed)
IMAGE=${IMAGE:-kaos-backend}
TAG=${TAG:-latest}
DOCKER_CONTEXT=${DOCKER_CONTEXT:-${PWD}}

# build docker image locally
echo "========================="
echo "| Build Docker Image... |"
echo "========================="
docker build -t ${IMAGE}:${TAG} -f ${DOCKERFILE} ${DOCKER_CONTEXT}
echo "+success"
