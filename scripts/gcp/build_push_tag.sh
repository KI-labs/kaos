#!/bin/bash
set -e

# define arguments
for i in "$@"
do
case ${i} in
    -i=*|--image=*)
    IMAGE="${i#*=}"
    shift # past argument=value
    ;;
    -p=*|--project=*)
    PROJECT_NAME="${i#*=}"
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
     -r=*|--region=*)
    REGION="${i#*=}"
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

# get the region defined in the current configuration
echo "==========================="
echo "| Configure GCP region... |"
echo "==========================="
if [[ -z "$REGION" ]]
    then
        REGION="eu"
fi
echo "+${REGION} being used"

# build docker image locally
echo "========================="
echo "| Build Docker Image... |"
echo "========================="
docker build -t ${IMAGE}:${TAG} -f ${DOCKER_FILE} ${DOCKER_CONTEXT} --build-arg PROVIDER=GCP

# define the full path of the docker image
echo "======================================"
echo "| Create GCP Registry Docker Path... |"
echo "======================================"
REGISTRY_NAME="${REGION}.gcr.io/${PROJECT_NAME}/${IMAGE}:${TAG}"
echo "+${REGISTRY_NAME}"

# push docker image to ECR
echo "========================"
echo "| Push Image to ECR... |"
echo "========================"
docker tag ${IMAGE}:${TAG} ${REGISTRY_NAME}
#  --config /dev/nul is necessary in case auth is preconfigured in ~/.docker/config.json. In such case the above docker login command will not work properly
docker --config /dev/nul push ${REGISTRY_NAME}
echo "+success"
