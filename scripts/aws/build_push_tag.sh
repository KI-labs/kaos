#!/bin/bash
set -e

check_deps () {
  test -f $(which docker) || error_exit "docker command not detected in path, please install it"
  test -f $(which aws) || error_exit "aws command not detected in path, please install it"
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

# get the account number associated with the current IAM credentials
echo "========================="
echo "| Verify AWS account... |"
echo "========================="
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
echo "+${ACCOUNT} being used"
if [ $? -ne 0 ]
then
    exit 255
fi

echo "+${REGION} being used"

# build docker image locally
echo "========================="
echo "| Build Docker Image... |"
echo "========================="
docker build -t ${IMAGE}:${TAG} -f ${DOCKER_FILE} ${DOCKER_CONTEXT} --build-arg PROVIDER=AWS

# define the full path of the docker image
echo "============================="
echo "| Create ECR Docker Path... |"
echo "============================="
ECR_NAME="${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com/${IMAGE}:${TAG}"
echo "+${ECR_NAME}"

# push docker image to ECR
echo "========================"
echo "| Push Image to ECR... |"
echo "========================"
docker tag ${IMAGE}:${TAG} ${ECR_NAME}
docker push ${ECR_NAME}
echo "+success"
