#!/bin/bash
set -e

function check_deps() {
  test -f $(which docker) || error_exit "docker command not detected in path, please install it"
  test -f $(which az) || error_exit "az command not detected in path, please install it"
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
    DOCKER_FILE="${i#*=}"
    shift # past argument=value
    ;;
    -u=*|--client_id=*)
    USERNAME="${i#*=}"
    shift # past argument=value
    ;;
    -p=*|--client_secret=*)
    PASSWORD="${i#*=}"
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
DOCKER_FILE=${DOCKER_FILE:-${DOCKER_CONTEXT}/Dockerfile}

echo "=============================="
echo "| Login to Azure Registry... |"
echo "=============================="
docker login "${IMAGE}.azurecr.io" -u "${USERNAME}" -p "${PASSWORD}"

# build docker image locally
echo "========================="
echo "| Build Docker Image... |"
echo "========================="
docker build -t ${IMAGE}:${TAG} -f ${DOCKER_FILE} ${DOCKER_CONTEXT} --build-arg PROVIDER=AZURE

# define the full path of the docker image
echo "============================="
echo "| Create ACR Docker Path... |"
echo "============================="
ACR_NAME="${IMAGE}.azurecr.io/${IMAGE}:${TAG}"
echo "+${ACR_NAME}"

# push docker image to ACR
echo "========================"
echo "| Push Image to ACR... |"
echo "========================"
docker tag ${IMAGE}:${TAG} ${ACR_NAME}
docker push ${ACR_NAME}
echo "+success"
